"""
AKIRA 4.0 Financial Heartbeat Module
Real-time profitability tracking and financial metrics for deployed projects.
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import redis

logger = logging.getLogger(__name__)

@dataclass
class ProjectFinancials:
    project_name: str
    deployment_date: str
    monthly_revenue: float  # Estimated or actual
    api_costs: float  # Monthly API costs
    infrastructure_costs: float  # Server, storage, etc.
    maintenance_hours: float  # Hours spent on maintenance
    hourly_rate: float  # Developer hourly rate for cost calculation
    
    @property
    def gross_profit(self) -> float:
        """Calculate gross profit (revenue - direct costs)."""
        return self.monthly_revenue - self.api_costs - self.infrastructure_costs
    
    @property
    def maintenance_cost(self) -> float:
        """Calculate maintenance cost."""
        return self.maintenance_hours * self.hourly_rate
    
    @property
    def net_profit(self) -> float:
        """Calculate net profit (gross profit - maintenance cost)."""
        return self.gross_profit - self.maintenance_cost
    
    @property
    def roi_percentage(self) -> float:
        """Calculate ROI percentage."""
        total_costs = self.api_costs + self.infrastructure_costs + self.maintenance_cost
        if total_costs == 0:
            return 0
        return (self.net_profit / total_costs) * 100
    
    @property
    def payback_period_days(self) -> float:
        """Calculate payback period in days."""
        daily_profit = self.net_profit / 30  # Assuming monthly metrics
        if daily_profit <= 0:
            return float('inf')
        return 30 / (daily_profit / self.net_profit) if self.net_profit > 0 else float('inf')

class FinancialHeartbeat:
    """
    Tracks financial metrics for all deployed projects in real-time.
    """
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.projects: Dict[str, ProjectFinancials] = {}
        self.load_projects()
    
    def add_project(self, project: ProjectFinancials) -> bool:
        """Add a new project to financial tracking."""
        try:
            self.projects[project.project_name] = project
            self._save_project(project)
            logger.info(f"Added project to financial tracking: {project.project_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add project: {str(e)}")
            return False
    
    def update_project_metrics(self, project_name: str, **kwargs) -> bool:
        """Update financial metrics for a project."""
        if project_name not in self.projects:
            logger.warning(f"Project not found: {project_name}")
            return False
        
        project = self.projects[project_name]
        
        # Update allowed fields
        allowed_fields = ['monthly_revenue', 'api_costs', 'infrastructure_costs', 'maintenance_hours']
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(project, field):
                setattr(project, field, value)
        
        self._save_project(project)
        logger.info(f"Updated metrics for project: {project_name}")
        return True
    
    def _save_project(self, project: ProjectFinancials) -> None:
        """Save project financials to Redis."""
        self.redis_client.hset(
            f"project_financials:{project.project_name}",
            "data",
            json.dumps(asdict(project))
        )
    
    def load_projects(self) -> None:
        """Load all projects from Redis."""
        try:
            keys = self.redis_client.keys("project_financials:*")
            for key in keys:
                data = self.redis_client.hget(key, "data")
                if data:
                    project_data = json.loads(data)
                    project = ProjectFinancials(**project_data)
                    self.projects[project.project_name] = project
            logger.info(f"Loaded {len(self.projects)} projects from storage")
        except Exception as e:
            logger.error(f"Failed to load projects: {str(e)}")
    
    def get_project_financials(self, project_name: str) -> Optional[Dict]:
        """Get financial summary for a specific project."""
        if project_name not in self.projects:
            return None
        
        project = self.projects[project_name]
        return {
            "project_name": project.project_name,
            "deployment_date": project.deployment_date,
            "monthly_revenue": project.monthly_revenue,
            "api_costs": project.api_costs,
            "infrastructure_costs": project.infrastructure_costs,
            "maintenance_cost": project.maintenance_cost,
            "gross_profit": project.gross_profit,
            "net_profit": project.net_profit,
            "roi_percentage": project.roi_percentage,
            "payback_period_days": project.payback_period_days
        }
    
    def get_portfolio_summary(self) -> Dict:
        """Get financial summary for the entire portfolio."""
        if not self.projects:
            return {
                "total_projects": 0,
                "total_monthly_revenue": 0,
                "total_api_costs": 0,
                "total_infrastructure_costs": 0,
                "total_maintenance_cost": 0,
                "portfolio_gross_profit": 0,
                "portfolio_net_profit": 0,
                "average_roi_percentage": 0,
                "profitable_projects": 0,
                "unprofitable_projects": 0
            }
        
        total_revenue = sum(p.monthly_revenue for p in self.projects.values())
        total_api_costs = sum(p.api_costs for p in self.projects.values())
        total_infra_costs = sum(p.infrastructure_costs for p in self.projects.values())
        total_maintenance_cost = sum(p.maintenance_cost for p in self.projects.values())
        
        gross_profit = total_revenue - total_api_costs - total_infra_costs
        net_profit = gross_profit - total_maintenance_cost
        
        profitable_count = sum(1 for p in self.projects.values() if p.net_profit > 0)
        unprofitable_count = len(self.projects) - profitable_count
        
        # Calculate average ROI
        roi_values = [p.roi_percentage for p in self.projects.values()]
        average_roi = sum(roi_values) / len(roi_values) if roi_values else 0
        
        return {
            "total_projects": len(self.projects),
            "total_monthly_revenue": total_revenue,
            "total_api_costs": total_api_costs,
            "total_infrastructure_costs": total_infra_costs,
            "total_maintenance_cost": total_maintenance_cost,
            "portfolio_gross_profit": gross_profit,
            "portfolio_net_profit": net_profit,
            "average_roi_percentage": average_roi,
            "profitable_projects": profitable_count,
            "unprofitable_projects": unprofitable_count,
            "profit_margin_percentage": (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        }
    
    def get_project_rankings(self) -> List[Dict]:
        """Get projects ranked by profitability."""
        rankings = []
        for project in self.projects.values():
            rankings.append({
                "project_name": project.project_name,
                "net_profit": project.net_profit,
                "roi_percentage": project.roi_percentage,
                "monthly_revenue": project.monthly_revenue
            })
        
        # Sort by net profit descending
        rankings.sort(key=lambda x: x["net_profit"], reverse=True)
        return rankings
    
    def get_financial_dashboard_data(self) -> Dict:
        """Get all data needed for the financial dashboard."""
        return {
            "timestamp": datetime.now().isoformat(),
            "portfolio_summary": self.get_portfolio_summary(),
            "project_rankings": self.get_project_rankings(),
            "individual_projects": {
                name: self.get_project_financials(name)
                for name in self.projects.keys()
            }
        }
    
    def estimate_project_profitability(self, 
                                      project_idea: str,
                                      estimated_revenue: float,
                                      estimated_api_costs: float,
                                      estimated_infra_costs: float,
                                      estimated_maintenance_hours: float,
                                      hourly_rate: float = 100) -> Dict:
        """
        Estimate profitability for a new project idea.
        Used during the Ideation phase to show financial projections.
        """
        temp_project = ProjectFinancials(
            project_name=f"[ESTIMATE] {project_idea}",
            deployment_date=datetime.now().isoformat(),
            monthly_revenue=estimated_revenue,
            api_costs=estimated_api_costs,
            infrastructure_costs=estimated_infra_costs,
            maintenance_hours=estimated_maintenance_hours,
            hourly_rate=hourly_rate
        )
        
        return {
            "project_idea": project_idea,
            "estimated_monthly_revenue": estimated_revenue,
            "estimated_api_costs": estimated_api_costs,
            "estimated_infrastructure_costs": estimated_infra_costs,
            "estimated_maintenance_cost": temp_project.maintenance_cost,
            "estimated_gross_profit": temp_project.gross_profit,
            "estimated_net_profit": temp_project.net_profit,
            "estimated_roi_percentage": temp_project.roi_percentage,
            "estimated_payback_period_days": temp_project.payback_period_days,
            "profitability_assessment": self._assess_profitability(temp_project)
        }
    
    def _assess_profitability(self, project: ProjectFinancials) -> str:
        """Assess and describe profitability of a project."""
        if project.net_profit < 0:
            return "🔴 Not Profitable - Costs exceed revenue"
        elif project.net_profit < 100:
            return "🟡 Low Profitability - Marginal returns"
        elif project.net_profit < 500:
            return "🟢 Moderate Profitability - Reasonable returns"
        elif project.net_profit < 2000:
            return "🟢 Good Profitability - Strong returns"
        else:
            return "🟢 Excellent Profitability - Exceptional returns"
    
    def get_ideation_financial_context(self, project_idea: str) -> str:
        """
        Generate financial context message for display during ideation.
        Shows real-time profitability estimates.
        """
        # Get portfolio context
        portfolio = self.get_portfolio_summary()
        
        message = (
            f"💰 **Financial Context for '{project_idea}'**\n\n"
            f"**Current Portfolio:**\n"
            f"- Total Projects: {portfolio['total_projects']}\n"
            f"- Monthly Revenue: ${portfolio['total_monthly_revenue']:,.2f}\n"
            f"- Net Profit: ${portfolio['portfolio_net_profit']:,.2f}\n"
            f"- Average ROI: {portfolio['average_roi_percentage']:.1f}%\n\n"
            f"**Profitability Benchmarks:**\n"
            f"- Median Project Profit: ${self._get_median_profit():,.2f}\n"
            f"- Top Project: {self._get_top_project()}\n"
        )
        
        return message
    
    def _get_median_profit(self) -> float:
        """Get median profit across all projects."""
        if not self.projects:
            return 0
        profits = sorted([p.net_profit for p in self.projects.values()])
        return profits[len(profits) // 2]
    
    def _get_top_project(self) -> str:
        """Get the most profitable project."""
        if not self.projects:
            return "None"
        top_project = max(self.projects.values(), key=lambda p: p.net_profit)
        return f"{top_project.project_name} (${top_project.net_profit:,.2f}/month)"

# Example usage
if __name__ == "__main__":
    heartbeat = FinancialHeartbeat()
    
    # Add sample projects
    project1 = ProjectFinancials(
        project_name="URL Monitoring SaaS",
        deployment_date=datetime.now().isoformat(),
        monthly_revenue=5000,
        api_costs=200,
        infrastructure_costs=300,
        maintenance_hours=10,
        hourly_rate=100
    )
    
    project2 = ProjectFinancials(
        project_name="Email Campaign Tool",
        deployment_date=datetime.now().isoformat(),
        monthly_revenue=8000,
        api_costs=500,
        infrastructure_costs=400,
        maintenance_hours=15,
        hourly_rate=100
    )
    
    heartbeat.add_project(project1)
    heartbeat.add_project(project2)
    
    # Get portfolio summary
    print("Portfolio Summary:")
    print(json.dumps(heartbeat.get_portfolio_summary(), indent=2))
    
    # Get financial dashboard
    print("\nFinancial Dashboard:")
    print(json.dumps(heartbeat.get_financial_dashboard_data(), indent=2, default=str))
    
    # Estimate new project
    print("\nEstimate for new project:")
    estimate = heartbeat.estimate_project_profitability(
        "Analytics Dashboard",
        estimated_revenue=6000,
        estimated_api_costs=300,
        estimated_infra_costs=250,
        estimated_maintenance_hours=12
    )
    print(json.dumps(estimate, indent=2))
