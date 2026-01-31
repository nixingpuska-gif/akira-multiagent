"""
AKIRA 4.0 Strict Test Observer v2
Fixed version that properly runs pytest and measures coverage.
"""

import subprocess
import json
import os
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    test_name: str
    status: str  # passed, failed, error
    duration: float
    error_message: Optional[str] = None

@dataclass
class ValidationReport:
    module_name: str
    timestamp: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    error_tests: int
    code_coverage: float
    quality_score: float
    is_production_ready: bool
    issues: List[str]
    recommendations: List[str]

class StrictTestObserverV2:
    """
    Fixed observer that properly validates code with pytest and coverage.
    """
    
    def __init__(self, project_root: str = "/home/ubuntu/akira_4_0"):
        self.project_root = project_root
        self.validation_history: List[ValidationReport] = []
        self.min_code_coverage = 0.80  # 80% minimum
        self.min_quality_score = 0.85  # 85% minimum
        self.strict_mode = True
    
    async def validate_module(self, module_name: str, code_path: str, test_path: str) -> ValidationReport:
        """Perform strict validation of a module."""
        logger.info(f"🔍 STRICT VALIDATION STARTING: {module_name}")
        logger.info("=" * 60)
        
        issues = []
        recommendations = []
        
        # Step 1: Syntax validation
        logger.info("Step 1: Syntax Validation...")
        syntax_ok, syntax_issues = self._validate_syntax(code_path)
        if not syntax_ok:
            issues.extend(syntax_issues)
            logger.error(f"❌ Syntax validation FAILED")
            return self._create_failed_report(module_name, issues, recommendations)
        logger.info("✅ Syntax validation PASSED")
        
        # Step 2: Import validation
        logger.info("Step 2: Import Validation...")
        import_ok, import_issues = self._validate_imports(code_path)
        if not import_ok:
            issues.extend(import_issues)
            logger.error(f"❌ Import validation FAILED")
            return self._create_failed_report(module_name, issues, recommendations)
        logger.info("✅ Import validation PASSED")
        
        # Step 3: Code quality analysis
        logger.info("Step 3: Code Quality Analysis...")
        quality_score, quality_issues = self._analyze_code_quality(code_path)
        if quality_issues:
            issues.extend(quality_issues)
        logger.info(f"Quality Score: {quality_score:.2f}/1.0")
        
        # Step 4: Run pytest with coverage
        logger.info("Step 4: Running Pytest with Coverage...")
        test_results, coverage = await self._run_pytest_with_coverage(test_path)
        
        passed = sum(1 for t in test_results if t.status == "passed")
        failed = sum(1 for t in test_results if t.status == "failed")
        errors = sum(1 for t in test_results if t.status == "error")
        
        logger.info(f"Test Results: {passed} passed, {failed} failed, {errors} errors")
        logger.info(f"Code Coverage: {coverage:.1f}%")
        
        if failed > 0 or errors > 0:
            issues.append(f"Test failures: {failed} failed, {errors} errors")
        
        if coverage < self.min_code_coverage * 100:
            issues.append(f"Code coverage {coverage:.1f}% below minimum {self.min_code_coverage*100:.0f}%")
            recommendations.append(f"Add tests to reach {self.min_code_coverage*100:.0f}% coverage")
        
        # Step 5: Integration test
        logger.info("Step 5: Integration Testing...")
        integration_ok, integration_issues = await self._test_integration(module_name, code_path)
        if not integration_ok:
            issues.extend(integration_issues)
            logger.warning(f"⚠️ Integration test issues detected")
        else:
            logger.info("✅ Integration test PASSED")
        
        # Step 6: Performance test
        logger.info("Step 6: Performance Testing...")
        perf_ok, perf_issues = await self._test_performance(module_name, code_path)
        if not perf_ok:
            issues.extend(perf_issues)
            logger.warning(f"⚠️ Performance issues detected")
        else:
            logger.info("✅ Performance test PASSED")
        
        # Step 7: Security check
        logger.info("Step 7: Security Analysis...")
        security_ok, security_issues = self._check_security(code_path)
        if not security_ok:
            issues.extend(security_issues)
            logger.error(f"❌ Security issues detected")
        else:
            logger.info("✅ Security check PASSED")
        
        # Generate final report
        is_production_ready = (
            quality_score >= self.min_quality_score and
            coverage >= self.min_code_coverage * 100 and
            failed == 0 and
            errors == 0 and
            security_ok and
            len(issues) == 0
        )
        
        report = ValidationReport(
            module_name=module_name,
            timestamp=datetime.now().isoformat(),
            total_tests=len(test_results),
            passed_tests=passed,
            failed_tests=failed,
            error_tests=errors,
            code_coverage=coverage,
            quality_score=quality_score,
            is_production_ready=is_production_ready,
            issues=issues,
            recommendations=recommendations
        )
        
        self.validation_history.append(report)
        
        # Print final verdict
        logger.info("=" * 60)
        if is_production_ready:
            logger.info("✅✅✅ VALIDATION PASSED - PRODUCTION READY ✅✅✅")
        else:
            logger.error("❌❌❌ VALIDATION FAILED - NOT PRODUCTION READY ❌❌❌")
        logger.info("=" * 60)
        
        return report
    
    def _validate_syntax(self, code_path: str) -> Tuple[bool, List[str]]:
        """Validate Python syntax."""
        try:
            with open(code_path, 'r') as f:
                code = f.read()
            compile(code, code_path, 'exec')
            return True, []
        except SyntaxError as e:
            return False, [f"Syntax error at line {e.lineno}: {e.msg}"]
        except Exception as e:
            return False, [f"Compilation error: {str(e)}"]
    
    def _validate_imports(self, code_path: str) -> Tuple[bool, List[str]]:
        """Validate that all imports can be resolved."""
        issues = []
        try:
            with open(code_path, 'r') as f:
                code = f.read()
            
            import_pattern = r'^\s*(?:from|import)\s+[\w\.]+'
            imports = re.findall(import_pattern, code, re.MULTILINE)
            
            for imp in imports:
                try:
                    if imp.startswith('from'):
                        module = imp.split()[1].split('.')[0]
                    else:
                        module = imp.split()[1].split('.')[0]
                    
                    __import__(module)
                except ImportError as e:
                    issues.append(f"Import error: {str(e)}")
            
            return len(issues) == 0, issues
        except Exception as e:
            return False, [f"Import validation error: {str(e)}"]
    
    def _analyze_code_quality(self, code_path: str) -> Tuple[float, List[str]]:
        """Analyze code quality metrics."""
        issues = []
        score = 1.0
        
        try:
            with open(code_path, 'r') as f:
                code = f.read()
            
            lines = code.split('\n')
            
            # Check for docstrings
            if '"""' not in code and "'''" not in code:
                issues.append("Missing module/class docstrings")
                score -= 0.1
            
            # Check for error handling
            if 'try:' not in code or 'except' not in code:
                issues.append("No error handling found")
                score -= 0.1
            
            # Check for logging
            if 'logger' not in code and 'logging' not in code:
                issues.append("No logging found")
                score -= 0.05
            
            # Check for type hints
            type_hint_count = len(re.findall(r'->\s*\w+', code))
            if type_hint_count == 0:
                issues.append("No type hints found")
                score -= 0.1
            
            # Check code length
            if len(lines) < 20:
                issues.append("Code too short (less than 20 lines)")
                score -= 0.2
            
            # Check for functions
            function_count = len(re.findall(r'def\s+\w+', code))
            if function_count == 0:
                issues.append("No functions defined")
                score -= 0.2
            
            # Check for __all__
            if '__all__' not in code:
                issues.append("No __all__ definition")
                score -= 0.1
            
            return max(score, 0.0), issues
            
        except Exception as e:
            return 0.0, [f"Quality analysis error: {str(e)}"]
    
    async def _run_pytest_with_coverage(self, test_path: str) -> Tuple[List[TestResult], float]:
        """Run pytest with coverage measurement."""
        results = []
        coverage = 0.0
        
        try:
            # Get test directory
            test_dir = os.path.dirname(test_path)
            
            # Run pytest
            cmd = [
                sys.executable, "-m", "pytest",
                test_path,
                "-v",
                "--tb=short",
                "--cov=" + test_dir,
                "--cov-report=json",
                "-x"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=test_dir
            )
            
            output = result.stdout + result.stderr
            
            # Parse test results
            test_pattern = r'(test_\w+)\s+(PASSED|FAILED|ERROR)'
            matches = re.findall(test_pattern, output)
            
            for test_name, status in matches:
                results.append(TestResult(
                    test_name=test_name,
                    status=status.lower(),
                    duration=0.0
                ))
            
            # Extract coverage from JSON report
            coverage_file = os.path.join(test_dir, ".coverage.json")
            if os.path.exists(coverage_file):
                try:
                    with open(coverage_file, 'r') as f:
                        cov_data = json.load(f)
                        coverage = cov_data.get('totals', {}).get('percent_covered', 0.0)
                except Exception as e:
                    logger.debug(f"Coverage extraction error: {str(e)}")
            
            logger.debug(f"Pytest output:\n{output[:500]}")
            
            return results, coverage
            
        except subprocess.TimeoutExpired:
            logger.error("Pytest timeout")
            return [TestResult("timeout", "error", 0.0, "Test execution timed out")], 0.0
        except Exception as e:
            logger.error(f"Pytest error: {str(e)}")
            return [TestResult("error", "error", 0.0, str(e))], 0.0
    
    async def _test_integration(self, module_name: str, code_path: str) -> Tuple[bool, List[str]]:
        """Test integration with other modules."""
        issues = []
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, code_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if not hasattr(module, '__all__'):
                issues.append("Module missing __all__ definition")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Integration test error: {str(e)}"]
    
    async def _test_performance(self, module_name: str, code_path: str) -> Tuple[bool, List[str]]:
        """Test performance characteristics."""
        issues = []
        
        try:
            import importlib.util
            import time
            
            spec = importlib.util.spec_from_file_location(module_name, code_path)
            module = importlib.util.module_from_spec(spec)
            
            start = time.time()
            spec.loader.exec_module(module)
            load_time = time.time() - start
            
            if load_time > 5.0:
                issues.append(f"Module load time too high: {load_time:.2f}s")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Performance test error: {str(e)}"]
    
    def _check_security(self, code_path: str) -> Tuple[bool, List[str]]:
        """Check for security issues."""
        issues = []
        
        try:
            with open(code_path, 'r') as f:
                code = f.read()
            
            dangerous_functions = ['eval', 'exec', '__import__', 'pickle.loads', 'os.system']
            for func in dangerous_functions:
                if func in code:
                    issues.append(f"Dangerous function found: {func}")
            
            if 'password' in code.lower() or 'api_key' in code.lower():
                if any(x in code for x in ['=', ':', '"""', "'''"]):
                    issues.append("Possible hardcoded secrets detected")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Security check error: {str(e)}"]
    
    def _create_failed_report(self, module_name: str, issues: List[str], recommendations: List[str]) -> ValidationReport:
        """Create a failed validation report."""
        return ValidationReport(
            module_name=module_name,
            timestamp=datetime.now().isoformat(),
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            error_tests=0,
            code_coverage=0.0,
            quality_score=0.0,
            is_production_ready=False,
            issues=issues,
            recommendations=recommendations
        )
    
    def get_validation_summary(self) -> Dict:
        """Get summary of all validations."""
        if not self.validation_history:
            return {"total_validations": 0}
        
        passed = sum(1 for r in self.validation_history if r.is_production_ready)
        failed = len(self.validation_history) - passed
        
        return {
            "total_validations": len(self.validation_history),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / len(self.validation_history) * 100) if self.validation_history else 0,
            "latest_validation": asdict(self.validation_history[-1]) if self.validation_history else None
        }
