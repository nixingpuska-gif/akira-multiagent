# Design Checklist - Чеклист Дизайна

## UX Designer Checklist

### Research Phase

- [ ] User research проведен
- [ ] User personas созданы
- [ ] User journey maps проработаны
- [ ] Competitor analysis выполнен
- [ ] Pain points идентифицированы

### Design Phase

- [ ] Information architecture определена
- [ ] User flows проработаны для всех ключевых сценариев
- [ ] Wireframes созданы для всех ключевых экранов
- [ ] Интерактивный прототип создан (Figma/Framer)
- [ ] Navigation patterns определены
- [ ] Interaction patterns определены

### Validation Phase

- [ ] Usability тестирование проведено
- [ ] Feedback собран и проанализирован
- [ ] Iterations сделаны на основе feedback
- [ ] Sign-off от Product Manager получен

---

## Visual Designer Checklist

### Preparation Phase

- [ ] Design brief прочитан и понят
- [ ] UX материалы изучены
- [ ] Research report прочитан
- [ ] Moodboard собран (референсы, inspiration)
- [ ] Style direction определен

### Design System Phase

- [ ] Цветовая палитра разработана
  - [ ] Primary colors (2-3 цвета)
  - [ ] Secondary colors (2-3 цвета)
  - [ ] Neutral colors (grayscale)
  - [ ] Semantic colors (success, error, warning, info)
  - [ ] Accessibility проверена (контрастность WCAG AA)
- [ ] Типографическая система определена
  - [ ] Font families выбраны (heading, body, mono)
  - [ ] Type scale определен (h1-h6, body, small, etc)
  - [ ] Line heights определены
  - [ ] Letter spacing определены
- [ ] Spacing/Grid система определена
  - [ ] Base unit (рекомендуется 8px)
  - [ ] Spacing scale (4, 8, 16, 24, 32, 48, 64...)
  - [ ] Grid columns (12-column grid)
- [ ] Border radius scale определен
- [ ] Shadow scale определен
- [ ] Icon style определен

### UI Kit Phase

- [ ] Buttons спроектированы (all states)
  - [ ] Primary button
  - [ ] Secondary button
  - [ ] Tertiary button
  - [ ] Ghost button
  - [ ] Disabled state
  - [ ] Loading state
  - [ ] Hover/Active/Focus states
- [ ] Inputs спроектированы
  - [ ] Text input
  - [ ] Textarea
  - [ ] Select/Dropdown
  - [ ] Checkbox
  - [ ] Radio button
  - [ ] Toggle/Switch
  - [ ] Error states
  - [ ] Disabled states
- [ ] Cards спроектированы
- [ ] Tables спроектированы
- [ ] Modals/Dialogs спроектированы
- [ ] Navigation components спроектированы
  - [ ] Header/Nav bar
  - [ ] Sidebar (если нужен)
  - [ ] Breadcrumbs
  - [ ] Tabs
  - [ ] Pagination
- [ ] Feedback components спроектированы
  - [ ] Tooltips
  - [ ] Alerts/Notifications
  - [ ] Toast messages
- [ ] Loading states спроектированы
  - [ ] Spinners
  - [ ] Progress bars
  - [ ] Skeleton screens
- [ ] Icons созданы или выбраны
  - [ ] Consistent style
  - [ ] All necessary icons
  - [ ] Multiple sizes if needed

### Dashboard/Data Visualization Phase

- [ ] Кастомные графики спроектированы (НЕ Chart.js defaults!)
  - [ ] Line charts
  - [ ] Bar charts
  - [ ] Pie/Donut charts
  - [ ] Area charts
  - [ ] Custom visualizations
- [ ] KPI/Metrics cards спроектированы
- [ ] Dashboard layout спроектирован
  - [ ] Data density оптимизирована
  - [ ] Visual hierarchy правильная
  - [ ] Responsive behavior определен

### Mockups Phase

- [ ] High-fidelity mockups созданы для всех экранов
- [ ] Pixel-perfect quality
- [ ] All components used from UI Kit
- [ ] Consistency проверена
- [ ] Visual hierarchy правильная
- [ ] Whitespace использован эффективно

### Micro-interactions Phase

- [ ] Hover states спроектированы
- [ ] Click/Tap feedback спроектирован
- [ ] Transitions спроектированы
- [ ] Loading animations спроектированы
- [ ] Animation specs документированы
  - [ ] Duration (ms)
  - [ ] Easing function
  - [ ] Properties to animate

### Dark Mode Phase

- [ ] Dark mode цветовая палитра создана
- [ ] Все компоненты адаптированы для dark mode
- [ ] Контрастность проверена (WCAG AA)
- [ ] Toggle mechanism спроектирован

### Responsive Design Phase

- [ ] Desktop mockups (1920px, 1440px)
- [ ] Tablet mockups (768px)
- [ ] Mobile mockups (375px, 414px)
- [ ] Breakpoints определены
- [ ] Responsive behavior задокументирован

### Documentation Phase

- [ ] Design System документирован
  - [ ] Colors with hex/RGB values
  - [ ] Typography specs
  - [ ] Spacing values
  - [ ] Component usage guidelines
- [ ] Figma файл организован
  - [ ] Pages/Frames логично структурированы
  - [ ] Components созданы и reusable
  - [ ] Naming consistent
- [ ] Handoff notes для Frontend Developer написаны
  - [ ] Asset export guidelines
  - [ ] Animation specifications
  - [ ] Interaction behaviors
  - [ ] Edge cases documented

### Quality Assurance Phase

- [ ] Дизайн НЕ похож на стандартные шаблоны ✓✓✓
  - [ ] Сравнение с Bootstrap/Material проведено
  - [ ] Сравнение со стандартными админками проведено
  - [ ] Уникальность подтверждена
- [ ] Профессионализм подтвержден
  - [ ] Все решения обоснованы
  - [ ] Color theory применена
  - [ ] Typography сбалансирована
  - [ ] Spacing консистентен
- [ ] Accessibility проверена
  - [ ] Color contrast WCAG AA
  - [ ] Focus states видимы
  - [ ] Interactive elements достаточно большие (min 44x44px)
- [ ] Performance considerations
  - [ ] Animations performant (60fps)
  - [ ] Assets optimized
- [ ] Sign-off получен
  - [ ] Validator reviewed
  - [ ] Product Manager approved
  - [ ] Ready for development

---

## Critical Success Factors

### ✅ Уникальность

Дизайн должен быть **узнаваемым** и **отличаться** от стандартных решений.

**Проверка**: Если показать дизайн без лого/текста - можно ли спутать с Bootstrap/Material/AdminLTE? Если да - **переделать**.

### ✅ Профессионализм

Дизайн должен быть уровня **Dribbble Top Shots** или **Behance Featured Projects**.

**Проверка**: Достаточно ли качества чтобы попасть в featured? Если нет - **улучшить**.

### ✅ Внимание к Деталям

Каждый пиксель на своем месте. Микроинтеракции на каждом элементе.

**Проверка**: Есть ли хоть один элемент без продуманного hover state? Если да - **доработать**.

---

**Примечание**: Этот checklist обязателен к использованию Visual Designer и UX Designer.
