/* AI Birja — SPA: биржевые данные + AI-агент + личный кабинет. Языки: RU / EN. */
"use strict";

// ---------------- i18n ----------------
const I18N = {
  ru: {
    "nav.home": "Главная", "nav.stocks": "Акции", "nav.commodities": "Товары", "nav.deals": "Реестр сделок",
    "nav.participants": "Участники", "nav.agent": "AI-агент", "nav.about": "О решении",
    "auth.choose": "Пожалуйста, выберите", "auth.login": "Логин", "auth.password": "Пароль", "auth.signin": "Войти",
    "auth.forgot": "Забыли пароль?", "auth.register": "Регистрация", "auth.cabinet": "Кабинет", "auth.enter": "Войти",
    "auth.name": "Имя и фамилия", "auth.create": "Создать аккаунт", "auth.logout": "Выйти", "auth.role": "Роль",
    "auth.err.invalid": "Неверный логин или пароль", "auth.err.exists": "Такой логин уже занят",
    "auth.err.short": "Логин — от 3 символов, пароль — от 6", "auth.forgot.text": "Восстановление пароля в прототипе недоступно — создайте новый аккаунт.",
    "role.investor": "Инвестор", "role.broker": "Брокер", "role.participant": "Участник торгов",
    "footer.text": "Прототип: сайт биржевых данных и AI-агент, который отвечает только на основе загруженных данных и проверяет каждое число.",
    "cov": "Данные: {n} сделок · {from} — {to}",
    "demo": "Котировки акций (UZSE) и товаров (UZEX), сделки с акциями, листинг, ликвидность и реестр брокеров — данные из файла «Данные торгов биржи UZEX.pdf» и с сайта биржи на 05.11.2026. Реестр товарных сделок, участники и курс USD — пока ДЕМО (синтетические): загрузите папку данных конкурса — python cli.py load <файл> --exchange UZEX",
    "util.issuer": "Эмитент", "util.trade": "Перейти к торговле", "util.src": "Котировки на {d}",
    "gov.title": "Государственные учреждения", "th.close": "Цена закрытия", "dt.daytrades": "Сделки за день",
    "dt.source": "Источник", "dt.qdate": "Дата котировки", "dt.ntrades": "Сделок за день", "dt.quote": "Котировка UZEX",
    "dt.noreg": "В реестре сделок нет сделок по этому товару.", "dt.reg": "Сделки в реестре ({n})",
    "f.contacts": "Наши контакты", "f.location": "Местоположение", "f.social": "Мы в социальных сетях",
    "f.contact_btn": "Связаться с нами", "f.hours": "Понедельник–Пятница 9:00–18:00",
    "f.address": "Адрес: укажите адрес команды", "f.about": "Прототип для конкурса: сайт биржевых данных и AI-агент, который отвечает только по данным. При использовании материалов ссылка на источники (uzex.uz, uzse.uz) обязательна.",
    "f.fill": "заполните", "f.sources": "Источники данных",
    "hero.title": "Биржевые данные и AI-агент, который не выдумывает",
    "hero.text": "Спросите на русском или узбекском — агент построит SQL-запрос к реестру сделок, покажет источник и проверит каждое число в ответе.",
    "hero.ph": "Например: какой товар принёс наибольший оборот в октябре 2026?", "hero.ask": "Спросить",
    "st.day": "Оборот за день", "st.month": "Оборот за месяц", "st.deals": "Сделок всего", "st.usd": "Курс USD", "st.usdData": "в данных конкурса",
    "st.daydeals": "{n} сделок · {d}", "st.monthdeals": "{n} сделок",
    "sec.trades": "Итоги торгов", "sec.listings": "Информация о ценных бумагах, включенных в биржевой котировальный лист",
    "sec.liq": "Уровни ликвидности акций, включенных в биржевой котировальный лист", "sec.monthly": "Оборот товарной биржи по месяцам",
    "sec.cats": "Оборот по группам товаров за последний месяц", "more": "Подробнее",
    "liq.asof": "По состоянию на {m} · {n} инструментов", "liq.high": "высоколиквидные", "liq.mid": "среднеликвидные",
    "liq.low": "низколиквидные", "liq.top": "Топ-10 высоколиквидных акций",
    "th.time": "Время", "th.code": "Код ЦБ", "th.logo": "Логотип", "th.issuer": "Эмитент", "th.type": "Тип ценной бумаги",
    "th.market": "Рынок", "th.board": "Площадка", "th.price": "Торговая цена", "th.qty": "Кол-во ЦБ", "th.volume": "Объём торгов",
    "th.ticker": "Тикер", "th.listed": "Дата включения", "th.currency": "Валюта", "th.nominal": "Номинальная стоимость", "th.count": "Кол-во",
    "th.last": "Последняя цена", "th.chg": "Изменение", "th.dayvol": "Объём за день", "th.vol30": "Объём 30 дн.",
    "th.cap": "Капитализация", "th.liq": "Ликвидность", "th.deal": "№ сделки", "th.date": "Дата", "th.product": "Товар",
    "th.category": "Группа", "th.amount": "Сумма", "th.seller": "Продавец", "th.buyer": "Покупатель", "th.region": "Регион",
    "th.section": "Тип / форма", "th.status": "Состояние", "f.status": "Состояние", "f.form": "Форма контракта", "f.market": "Тип контракта",
    "ds": "Реестр сделок — набор данных конкурса «uzex_spot_data» (данные вымышленные, формат реестра товарно-сырьевой биржи): {n} сделок за {a} — {b}. Обороты — в UZS (USD-сделки по курсу на дату сделки), аннулированные (неоплаченные) сделки в обороты не входят.",
    "th.source": "Источник", "th.deals": "Сделок", "th.turnover": "Оборот", "th.month": "Месяц",
    "th.vwap": "Средневзв. цена", "th.low": "Мин.", "th.high": "Макс.", "th.name": "Наименование", "th.role": "Роль",
    "th.inn": "ИНН", "th.license": "Лицензия", "th.unit": "Ед.", "th.brokers": "Брокеры (прод./пок.)",
    "type.common": "Простые акции", "type.pref": "Прив. акции",
    "stocks.title": "Акции", "stocks.text": "Все ценные бумаги котировального листа: цены, изменение, объёмы и ликвидность за 12 месяцев.",
    "stocks.search": "Поиск по тикеру или эмитенту", "all": "Все",
    "com.title": "Товарная биржа", "com.text": "Котировки биржевых товаров: средневзвешенная цена последнего торгового дня и изменение к предыдущему.",
    "deals.title": "Реестр биржевых сделок", "deals.text": "Каждая сделка — с номером, состоянием, участниками, брокерами, источником и строкой файла.",
    "f.search": "Поиск: товар, участник, № сделки или ИНН", "f.from": "С даты", "f.to": "По дату", "f.category": "Группа", "f.region": "Регион",
    "f.product": "Товар", "f.reset": "Сбросить", "f.csv": "Скачать CSV",
    "pager": "Найдено {n} сделок · сумма {s}", "prev": "← Назад", "next": "Вперёд →", "page": "Стр. {p} из {t}",
    "dt.issuer": "Эмитент", "dt.isin": "ISIN", "dt.type": "Тип", "dt.nominal": "Номинал", "dt.shares": "Кол-во акций",
    "dt.listed": "В листинге с", "dt.cap": "Капитализация", "dt.liq": "Ликвидность (мес. с торгами из 12)",
    "dt.chart": "Цена закрытия по дням", "dt.trades": "Последние сделки", "dt.watch": "В избранное", "dt.watched": "В избранном",
    "dt.ask": "Спросить агента об этом", "dt.cchart": "Средневзвешенная цена по месяцам", "dt.buyers": "Крупнейшие покупатели",
    "dt.period": "Период торгов", "dt.monthly": "Статистика по месяцам", "dt.totq": "Объём, всего", "back": "← Назад",
    "part.title": "Участники торгов", "part.text": "Справочники участников и брокеров из папки данных.", "part.brokers": "Брокеры", "part.list": "Участники",
    "role.seller": "Продавец", "role.buyer": "Покупатель",
    "ag.title": "AI-агент по биржевым данным", "ag.text": "Отвечает только по данным. Если ответа в данных нет — так и скажет.",
    "ag.ph": "Задайте вопрос на русском, узбекском или английском…", "ag.send": "Отправить", "ag.thinking": "Ищу в данных",
    "ag.ok": "Все числа подтверждены данными", "ag.no": "Не все числа подтверждены: ", "ag.sql": "SQL-запросы ({n})",
    "ag.ev": "Данные, на которых основан ответ", "ag.time": "Время ответа: {s} с", "ag.examples": "Примеры вопросов",
    "ag.rules": "Как агент гарантирует точность", "ag.clear": "Новый диалог",
    "ag.r1": "Каждое вычисление — SQL-запрос к базе (только чтение).",
    "ag.r2": "Каждое число в ответе автоматически сверяется с результатами запросов.",
    "ag.r3": "Если число не подтверждено — модель переписывает ответ.",
    "ag.r4": "Нет данных — агент прямо говорит «в данных ответа нет».",
    "ag.r5": "Показываются SQL-запросы и строки-источники.",
    "ag.err": "Ошибка: ", "ag.hello": "Здравствуйте! Я отвечаю на вопросы по реестру биржевых сделок, акциям, участникам, брокерам и курсу доллара. Задайте вопрос.",
    "cab.title": "Личный кабинет", "cab.watch": "Избранное", "cab.hist": "История вопросов агенту", "cab.upload": "Загрузка данных",
    "cab.upload.text": "Загрузите файл сделок (CSV / XLSX / JSON / HTML) — колонки распознаются автоматически.",
    "cab.uploaded": "Загружено: {f} — новых сделок: {n}", "cab.nowatch": "Добавьте акции или товары в избранное (★).",
    "cab.nohist": "Вы ещё не задавали вопросов.", "cab.since": "С нами с {d}",
    "about.title": "О решении", "notfound": "Страница не найдена", "loading": "Загрузка…",
    "watch.login": "Войдите, чтобы добавить в избранное",
    "search": "Поиск", "search.ph": "Тикер, эмитент, товар, участник или раздел…", "search.ask": "Спросить AI-агента",
    "trades.text": "Последние сделки с акциями: время, код ЦБ, эмитент, цена, количество и объём.",
    "usd.title": "Курс доллара", "usd.text": "Курс USD/UZS из папки данных — агент использует его для пересчёта сумм в доллары.",
    "info.text": "Этот раздел есть в структуре сайта биржи, но в папке данных конкурса нет его документов, поэтому прототип не заполняет его текстом (мы ничего не выдумываем). Все рыночные данные — акции, товары, сделки, участники, брокеры, курс — доступны в соответствующих разделах и через AI-агента.",
    "ag.engine.claude": "Claude + SQL", "ag.engine.offline": "Офлайн-движок: правила → SQL (без LLM)",
  },
  en: {
    "nav.home": "Home", "nav.stocks": "Stocks", "nav.commodities": "Commodities", "nav.deals": "Deal registry",
    "nav.participants": "Participants", "nav.agent": "AI agent", "nav.about": "Solution",
    "auth.choose": "Please choose", "auth.login": "Login", "auth.password": "Password", "auth.signin": "Sign in",
    "auth.forgot": "Forgot password?", "auth.register": "Sign up", "auth.cabinet": "Account", "auth.enter": "Sign in",
    "auth.name": "Full name", "auth.create": "Create account", "auth.logout": "Log out", "auth.role": "Role",
    "auth.err.invalid": "Wrong login or password", "auth.err.exists": "This login is already taken",
    "auth.err.short": "Login needs 3+ characters, password 6+", "auth.forgot.text": "Password recovery is not available in the prototype — please create a new account.",
    "role.investor": "Investor", "role.broker": "Broker", "role.participant": "Trading participant",
    "footer.text": "Prototype: an exchange data website and an AI agent that answers only from the loaded data and checks every number.",
    "cov": "Data: {n} deals · {from} — {to}",
    "demo": "Share (UZSE) and commodity (UZEX) quotes, share trades, listing, liquidity and the broker registry come from the file \"Данные торгов биржи UZEX.pdf\" and the exchange site as of 05.11.2026. The commodity deal registry, participants and USD rate are still DEMO (synthetic): load the contest data folder — python cli.py load <file> --exchange UZEX",
    "util.issuer": "Issuer", "util.trade": "Go to trading", "util.src": "Quotes as of {d}",
    "gov.title": "Government institutions", "th.close": "Close price", "dt.daytrades": "Trades during the day",
    "dt.source": "Source", "dt.qdate": "Quote date", "dt.ntrades": "Trades today", "dt.quote": "UZEX quote",
    "dt.noreg": "The deal registry has no deals for this commodity.", "dt.reg": "Registry deals ({n})",
    "f.contacts": "Contacts", "f.location": "Location", "f.social": "Social media",
    "f.contact_btn": "Contact us", "f.hours": "Monday–Friday 9:00–18:00",
    "f.address": "Address: add your team address", "f.about": "Contest prototype: an exchange data website and an AI agent that answers only from the data. When using materials, a reference to the sources (uzex.uz, uzse.uz) is required.",
    "f.fill": "fill in", "f.sources": "Data sources",
    "hero.title": "Exchange data and an AI agent that never makes things up",
    "hero.text": "Ask in Russian, Uzbek or English — the agent writes SQL against the deal registry, shows its sources and checks every number in the answer.",
    "hero.ph": "e.g. Which commodity had the highest turnover in October 2026?", "hero.ask": "Ask",
    "st.day": "Daily turnover", "st.month": "Monthly turnover", "st.deals": "Total deals", "st.usd": "USD rate", "st.usdData": "in contest data",
    "st.daydeals": "{n} deals · {d}", "st.monthdeals": "{n} deals",
    "sec.trades": "Trading results", "sec.listings": "Securities included in the exchange quotation list",
    "sec.liq": "Liquidity levels of shares in the quotation list", "sec.monthly": "Commodity exchange turnover by month",
    "sec.cats": "Turnover by commodity group, last month", "more": "More",
    "liq.asof": "As of {m} · {n} instruments", "liq.high": "high liquidity", "liq.mid": "medium liquidity",
    "liq.low": "low liquidity", "liq.top": "Top-10 most liquid shares",
    "th.time": "Time", "th.code": "Code", "th.logo": "Logo", "th.issuer": "Issuer", "th.type": "Security type",
    "th.market": "Market", "th.board": "Board", "th.price": "Price", "th.qty": "Quantity", "th.volume": "Volume",
    "th.ticker": "Ticker", "th.listed": "Listed on", "th.currency": "Currency", "th.nominal": "Nominal value", "th.count": "Shares",
    "th.last": "Last price", "th.chg": "Change", "th.dayvol": "Day volume", "th.vol30": "30-day volume",
    "th.cap": "Market cap", "th.liq": "Liquidity", "th.deal": "Deal #", "th.date": "Date", "th.product": "Commodity",
    "th.category": "Group", "th.amount": "Amount", "th.seller": "Seller", "th.buyer": "Buyer", "th.region": "Region",
    "th.section": "Type / form", "th.status": "Status", "f.status": "Status", "f.form": "Contract form", "f.market": "Contract type",
    "ds": "The deal registry is the contest dataset \"uzex_spot_data\" (fictional data in the commodity exchange registry format): {n} deals, {a} — {b}. Turnover is in UZS (USD deals at the rate on the deal date); cancelled (unpaid) deals are not counted in turnover.",
    "th.source": "Source", "th.deals": "Deals", "th.turnover": "Turnover", "th.month": "Month",
    "th.vwap": "VWAP", "th.low": "Low", "th.high": "High", "th.name": "Name", "th.role": "Role",
    "th.inn": "TIN", "th.license": "License", "th.unit": "Unit", "th.brokers": "Brokers (sell/buy)",
    "type.common": "Common shares", "type.pref": "Preferred shares",
    "stocks.title": "Stocks", "stocks.text": "All securities on the quotation list: prices, change, volumes and 12-month liquidity.",
    "stocks.search": "Search by ticker or issuer", "all": "All",
    "com.title": "Commodity exchange", "com.text": "Commodity quotes: volume-weighted price on the last trading day and change vs. the previous one.",
    "deals.title": "Exchange deal registry", "deals.text": "Every deal with its number, status, parties, brokers, source file and row.",
    "f.search": "Search: commodity, party, deal # or TIN", "f.from": "From", "f.to": "To", "f.category": "Group", "f.region": "Region",
    "f.product": "Commodity", "f.reset": "Reset", "f.csv": "Download CSV",
    "pager": "{n} deals found · total {s}", "prev": "← Prev", "next": "Next →", "page": "Page {p} of {t}",
    "dt.issuer": "Issuer", "dt.isin": "ISIN", "dt.type": "Type", "dt.nominal": "Nominal", "dt.shares": "Shares outstanding",
    "dt.listed": "Listed since", "dt.cap": "Market cap", "dt.liq": "Liquidity (months traded of 12)",
    "dt.chart": "Daily closing price", "dt.trades": "Latest trades", "dt.watch": "Add to watchlist", "dt.watched": "In watchlist",
    "dt.ask": "Ask the agent about it", "dt.cchart": "Volume-weighted price by month", "dt.buyers": "Largest buyers",
    "dt.period": "Trading period", "dt.monthly": "Monthly statistics", "dt.totq": "Total quantity", "back": "← Back",
    "part.title": "Trading participants", "part.text": "Participant and broker reference lists from the data folder.", "part.brokers": "Brokers", "part.list": "Participants",
    "role.seller": "Seller", "role.buyer": "Buyer",
    "ag.title": "AI agent for exchange data", "ag.text": "Answers only from the data. If the data has no answer, it says so.",
    "ag.ph": "Ask in Russian, Uzbek or English…", "ag.send": "Send", "ag.thinking": "Searching the data",
    "ag.ok": "All numbers verified against the data", "ag.no": "Some numbers not verified: ", "ag.sql": "SQL queries ({n})",
    "ag.ev": "Data the answer is based on", "ag.time": "Answered in {s} s", "ag.examples": "Example questions",
    "ag.rules": "How the agent stays accurate", "ag.clear": "New chat",
    "ag.r1": "Every calculation is a read-only SQL query.",
    "ag.r2": "Every number in the answer is automatically checked against query results.",
    "ag.r3": "If a number is not confirmed, the model rewrites the answer.",
    "ag.r4": "No data — the agent says so plainly.",
    "ag.r5": "SQL queries and source rows are shown.",
    "ag.err": "Error: ", "ag.hello": "Hello! I answer questions about the deal registry, stocks, participants, brokers and the USD rate. Ask away.",
    "cab.title": "Personal account", "cab.watch": "Watchlist", "cab.hist": "Questions you asked the agent", "cab.upload": "Upload data",
    "cab.upload.text": "Upload a deals file (CSV / XLSX / JSON / HTML) — columns are mapped automatically.",
    "cab.uploaded": "Uploaded: {f} — new deals: {n}", "cab.nowatch": "Add stocks or commodities to your watchlist (★).",
    "cab.nohist": "You haven't asked anything yet.", "cab.since": "Member since {d}",
    "about.title": "Solution", "notfound": "Page not found", "loading": "Loading…",
    "watch.login": "Sign in to use the watchlist",
    "search": "Search", "search.ph": "Ticker, issuer, commodity, participant or section…", "search.ask": "Ask the AI agent",
    "trades.text": "Latest share trades: time, code, issuer, price, quantity and volume.",
    "usd.title": "USD rate", "usd.text": "USD/UZS rate from the data folder — the agent uses it to convert amounts to dollars.",
    "info.text": "This section exists in the exchange site structure, but the contest data folder has no documents for it, so the prototype doesn't fill it with text (we don't make anything up). All market data — stocks, commodities, deals, participants, brokers, rate — is available in the matching sections and through the AI agent.",
    "ag.engine.claude": "Claude + SQL", "ag.engine.offline": "Offline engine: rules → SQL (no LLM)",
  },
};
const EXAMPLES = [
  ["RU", "Какой товар принёс наибольший оборот в октябре 2026 года?"],
  ["UZ", "2025-yilda Mis katodi bo'yicha nechta bitim tuzilgan va jami summasi qancha?"],
  ["RU", "Топ-5 покупателей дизельного топлива за 2024 год по сумме"],
  ["UZ", "Qaysi broker sotuvchi tomonida eng ko'p bitim qilgan?"],
  ["RU", "Средняя цена Polipropilen B-310 по месяцам в 2026 году"],
  ["UZ", "IPTB aksiyasining oktyabr oyidagi savdo hajmi qancha?"],
  ["EN", "What was the total turnover in USD in September 2026 using the daily USD rate?"],
  ["RU", "Сколько сделок было по золоту в 2023 году?"],
];

let LANG = new URLSearchParams(location.search).get("lang") || store("lang") || "ru";
if (!I18N[LANG]) LANG = "ru";
const t = (k, v = {}) => (I18N[LANG][k] ?? I18N.ru[k] ?? k).replace(/\{(\w+)\}/g, (_, x) => v[x] ?? "");

function store(k, v) {
  try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch { return null; }
}

// ---------------- helpers ----------------
const $ = (s, el = document) => el.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
function fmt(n, d) {
  if (n === null || n === undefined || n === "") return "—";
  n = Number(n);
  if (d === undefined) d = Math.abs(n) < 100 && !Number.isInteger(n) ? 2 : (Number.isInteger(n) ? 0 : 2);
  return n.toLocaleString("ru-RU", { minimumFractionDigits: d, maximumFractionDigits: d }).replace(/ /g, " ").replace(",", ".");
}
function short(n) {
  if (n === null || n === undefined) return "—";
  const a = Math.abs(n), u = LANG === "ru" ? ["трлн", "млрд", "млн", "тыс"] : ["T", "B", "M", "K"];
  if (a >= 1e12) return fmt(n / 1e12, 2) + " " + u[0];
  if (a >= 1e9) return fmt(n / 1e9, 2) + " " + u[1];
  if (a >= 1e6) return fmt(n / 1e6, 2) + " " + u[2];
  return fmt(n);
}
const cls = v => v > 0 ? "up" : v < 0 ? "down" : "flat";
const sign = v => v > 0 ? "+" : "";
const dmy = s => s ? s.slice(0, 10).split("-").reverse().join(".") : "—";
const ini = s => (s || "?").replace(/[<>"']/g, "").replace(/^(AJ|AT|ATB)\s+/, "").trim().slice(0, 2).toUpperCase();
const liqBadge = m => m == null ? `<span class="muted">—</span>` : `<span class="badge b-${m >= 10 ? "high" : m >= 6 ? "mid" : "low"}">${m}/12</span>`;
const typeName = s => I18N[LANG]["type." + s] || esc(s);
const arrow = c => c > 0 ? `<svg class="tk-arrow" width="12" height="28" viewBox="0 0 12 28"><path d="M6 27V3M1 8l5-6 5 6" stroke="#1fa83b" stroke-width="2" fill="none"/></svg>`
  : c < 0 ? `<svg class="tk-arrow" width="12" height="28" viewBox="0 0 12 28"><path d="M6 1v24M1 20l5 6 5-6" stroke="#ff2b2b" stroke-width="2" fill="none"/></svg>` : "<span></span>";

async function api(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  const tok = store("token");
  if (tok) headers.Authorization = "Bearer " + tok;
  if (opts.json) { headers["Content-Type"] = "application/json"; opts.body = JSON.stringify(opts.json); }
  const r = await fetch(path, { ...opts, headers });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw Object.assign(new Error(d.detail || r.statusText), { status: r.status, detail: d.detail });
  return d;
}
const cache = {};
const cached = (k, f) => cache[k] ||= f().catch(e => { delete cache[k]; throw e; });

// ---------------- state ----------------
const S = { user: null, watch: [], chat: [] };
async function loadMe() {
  if (!store("token")) { S.user = null; S.watch = []; return; }
  try { const d = await api("/api/me"); S.user = d.user; S.watch = d.watchlist; }
  catch { store("token", null); S.user = null; S.watch = []; }
}
const isWatched = (kind, code) => S.watch.some(w => w.kind === kind && w.code === code);
async function toggleWatch(kind, code) {
  if (!S.user) { openPop(); return; }
  S.watch = await api("/api/me/watch", { method: "POST", json: { kind, code } });
}
function starBtn(kind, code) {
  return `<button class="star ${isWatched(kind, code) ? "on" : ""}" data-watch="${kind}:${esc(code)}" title="${t("dt.watch")}">★</button>`;
}
document.addEventListener("click", async e => {
  const b = e.target.closest("[data-watch]");
  if (!b) return;
  e.stopPropagation(); e.preventDefault();
  const [kind, code] = b.dataset.watch.split(":");
  await toggleWatch(kind, code);
  document.querySelectorAll(`[data-watch="${kind}:${CSS.escape(code)}"]`).forEach(x => {
    x.classList.toggle("on", isWatched(kind, code));
    if (x.dataset.label) x.textContent = isWatched(kind, code) ? "★ " + t("dt.watched") : "☆ " + t("dt.watch");
  });
});

// ---------------- chrome: tape, header, i18n ----------------
function applyI18n() {
  document.documentElement.lang = LANG;
  document.querySelectorAll("[data-i18n]").forEach(el => el.textContent = t(el.dataset.i18n));
  document.querySelectorAll("[data-i18n-ph]").forEach(el => el.placeholder = t(el.dataset.i18nPh));
  document.querySelectorAll(".lang button").forEach(b => b.classList.toggle("on", b.dataset.lang === LANG));
  $("#acctLabel").textContent = S.user ? S.user.name : t("auth.enter");
}
document.querySelectorAll(".lang button").forEach(b => b.onclick = () => { LANG = b.dataset.lang; store("lang", LANG); applyI18n(); buildNav(); renderTape(); footer(); route(); });

let TAPE = [];
async function renderTape() {
  try { TAPE = await cached("ticker", () => api("/api/market/ticker")); } catch { return; }
  const items = TAPE.map(x => `
    <a class="tk" href="#/commodity/${encodeURIComponent(x.code)}" title="${esc(x.name)} · ${dmy(x.date)}">
      <span class="tk-name">${esc(x.name)}</span>${arrow(x.change)}
      <span class="tk-price num">${fmt(x.price, 2)}</span>
      <span class="tk-chg num ${cls(x.change)}">${sign(x.change)}${fmt(x.change, 2)}(${fmt(Math.abs(x.change_pct), 2)}%)</span>
    </a>`).join("");
  $("#tapeTrack").innerHTML = items + items;
  const d = TAPE.map(x => x.date).filter(Boolean).sort().pop();
  const src = document.querySelector(".util-src");
  if (src) src.textContent = d ? t("util.src", { d: dmy(d) }) : "";
}

function openPop() { $("#loginPop").hidden = false; $("#popLogin [name=role]").focus(); }
$("#acctBtn").onclick = e => {
  e.stopPropagation();
  if (S.user) { location.hash = "#/cabinet"; return; }
  $("#loginPop").hidden ? openPop() : ($("#loginPop").hidden = true);
};
document.addEventListener("click", e => { if (!e.target.closest(".acct")) $("#loginPop").hidden = true; });
$("#popLogin").onsubmit = async e => {
  e.preventDefault();
  const f = new FormData(e.target), err = $(".form-err", e.target);
  try {
    const d = await api("/api/auth/login", { method: "POST", json: Object.fromEntries(f) });
    store("token", d.token); await loadMe(); $("#loginPop").hidden = true; e.target.reset(); applyI18n();
    location.hash = "#/cabinet"; route();
  } catch (x) { err.hidden = false; err.textContent = t("auth.err." + (x.detail || "invalid")); }
};
$("#popLogin").addEventListener("click", e => { if (e.target.closest(".pop-link")) $("#loginPop").hidden = true; });
$("#burger").onclick = () => $("#nav").classList.toggle("open");

// Kontaktlar: jamoangiz ma'lumotlarini shu yerga yozing (hozircha namunaviy raqamlar)
const CONTACTS = { phone1: "+998 (__) ___-__-__", phone2: "+998 (__) ___-__-__", email: "info@ai-birja.uz", telegram: "#", facebook: "#", x: "#", linkedin: "#", instagram: "#", bot: "#/agent" };
const ICO = {
  phone: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
  mail: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
  pin: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>',
  clock: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
  fb: '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H8v4h2v8h4v-8h3l1-4h-4V8z"/></svg>',
  tg: '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M21 4 2.5 11.2c-.9.4-.9 1.5 0 1.8l4.6 1.5 1.8 5.6c.2.7 1.1.9 1.6.4l2.6-2.4 4.8 3.5c.6.4 1.4.1 1.6-.6L22.9 5.2c.3-.9-.6-1.6-1.9-1.2zM9.6 14.3l8.2-7.2-6.4 8.3-.3 3-1.5-4.1z"/></svg>',
  x: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.5 3h3.3l-7.2 8.2L22 21h-6.6l-5.2-6.6L4.3 21H1l7.7-8.8L1 3h6.8l4.7 6.1zm-1.2 16.1h1.8L6.8 4.8H4.9z"/></svg>',
  in: '<svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor"><path d="M4 9h4v12H4zM6 3a2 2 0 1 1 0 4 2 2 0 0 1 0-4zm5 6h4v1.7c.6-1 1.9-2 3.9-2C22 8.7 22 11.3 22 14v7h-4v-6.2c0-1.5 0-3.3-2-3.3s-2.3 1.6-2.3 3.2V21h-4z"/></svg>',
  ig: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
  bot: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 4v4M9 13h.01M15 13h.01"/></svg>',
};
async function footer() {
  let cov = "";
  try {
    const d = await cached("data", () => api("/api/data"));
    cov = t("cov", { n: fmt(d.total_rows), from: dmy(d.date_range[0]), to: dmy(d.date_range[1]) });
  } catch {}
  const C = CONTACTS;
  $("#ftr").innerHTML = `<div class="wrap">
    <div class="ftr-grid">
      <div class="ftr-about"><h3>AI BIRJA</h3><p>${t("f.about")}</p><a class="btn ftr-btn" href="#/agent">${t("f.contact_btn")} →</a></div>
      <div><h4>${t("f.contacts")}</h4>
        <a class="ftr-row" href="tel:${C.phone1.replace(/[^+\d]/g, "")}">${ICO.phone}<span>${esc(C.phone1)}</span></a>
        <a class="ftr-row" href="tel:${C.phone2.replace(/[^+\d]/g, "")}">${ICO.phone}<span>${esc(C.phone2)}</span></a>
        <a class="ftr-row" href="mailto:${esc(C.email)}">${ICO.mail}<span>${esc(C.email)}</span></a></div>
      <div><h4>${t("f.location")}</h4>
        <div class="ftr-row">${ICO.pin}<span>${t("f.address")}</span></div>
        <div class="ftr-row">${ICO.clock}<span>${t("f.hours")}</span></div></div>
      <div><h4>${t("f.social")}</h4><div class="soc">
        <a href="${C.facebook}" aria-label="Facebook">${ICO.fb}</a><a href="${C.telegram}" aria-label="Telegram">${ICO.tg}</a><a href="${C.x}" aria-label="X">${ICO.x}</a>
        <a href="${C.linkedin}" aria-label="LinkedIn">${ICO.in}</a><a href="${C.instagram}" aria-label="Instagram">${ICO.ig}</a><a href="${C.bot}" aria-label="AI bot">${ICO.bot}</a></div>
        <h4 style="margin-top:22px">${t("f.sources")}</h4>
        <a class="ftr-row" href="https://uzex.uz" target="_blank" rel="noopener">uzex.uz</a><a class="ftr-row" href="https://uzse.uz" target="_blank" rel="noopener">uzse.uz</a></div>
    </div>
    <div class="ftr-bottom"><span>© 2026 AI Birja</span><span>${esc(cov)}</span><a href="#/about">${t("nav.about")}</a></div>
  </div>`;
}
async function demoNote(registry = false) {
  try {
    const d = await cached("data", () => api("/api/data"));
    if (Object.keys(d.exchanges).some(x => /DEMO/i.test(x))) return `<div class="demo-note">⚠ ${t("demo")}</div>`;
    if (registry && d.sources.some(s => /uzex_spot_data/.test(s.url || "")))
      return `<div class="demo-note">ℹ ${t("ds", { n: fmt(d.total_rows), a: dmy(d.date_range[0]), b: dmy(d.date_range[1]) })}</div>`;
    return "";
  } catch { return ""; }
}

// ---------------- charts (inline SVG) ----------------
function lineChart(points, { area = true, color = "#0b5cff", fmtY = v => short(v), fmtX = x => x } = {}) {
  if (!points.length) return `<div class="empty">—</div>`;
  const W = 900, H = 300, P = { l: 92, r: 16, t: 14, b: 28 };
  const ys = points.map(p => p.y), min = Math.min(...ys), max = Math.max(...ys), pad = (max - min) * .08 || max * .05 || 1;
  const y0 = min - pad, y1 = max + pad;
  const X = i => P.l + (points.length === 1 ? 0 : i / (points.length - 1)) * (W - P.l - P.r);
  const Y = v => P.t + (1 - (v - y0) / (y1 - y0)) * (H - P.t - P.b);
  const d = points.map((p, i) => `${i ? "L" : "M"}${X(i).toFixed(1)},${Y(p.y).toFixed(1)}`).join("");
  let grid = "";
  for (let k = 0; k <= 4; k++) {
    const v = y0 + (y1 - y0) * k / 4, y = Y(v);
    grid += `<line x1="${P.l}" x2="${W - P.r}" y1="${y}" y2="${y}" stroke="#e3e8f2"/><text x="${P.l - 8}" y="${y + 4}" text-anchor="end">${fmtY(v)}</text>`;
  }
  const step = Math.max(1, Math.ceil(points.length / 8));
  points.forEach((p, i) => { if (i % step === 0) grid += `<text x="${X(i)}" y="${H - 8}" text-anchor="middle">${esc(fmtX(p.x))}</text>`; });
  const id = "g" + Math.random().toString(36).slice(2, 7);
  return `<svg class="chart" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" data-pts='${esc(JSON.stringify(points.map((p, i) => [X(i), Y(p.y), p.x, p.label ?? fmt(p.y)])))}'>
    <defs><linearGradient id="${id}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${color}" stop-opacity=".18"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></linearGradient></defs>
    ${grid}${area ? `<path d="${d}L${X(points.length - 1)},${H - P.b}L${P.l},${H - P.b}Z" fill="url(#${id})"/>` : ""}
    <path d="${d}" fill="none" stroke="${color}" stroke-width="2" vector-effect="non-scaling-stroke"/>
    <circle class="hov" r="4" fill="${color}" stroke="#fff" stroke-width="2" style="display:none"/>
  </svg>`;
}
function barChart(points, { color = "#0b5cff", fmtX = x => x } = {}) {
  if (!points.length) return "";
  const W = 900, H = 260, P = { l: 92, r: 10, t: 10, b: 28 }, max = Math.max(...points.map(p => p.y)) * 1.08;
  const bw = (W - P.l - P.r) / points.length;
  let g = "";
  for (let k = 0; k <= 4; k++) { const v = max * k / 4, y = P.t + (1 - k / 4) * (H - P.t - P.b); g += `<line x1="${P.l}" x2="${W - P.r}" y1="${y}" y2="${y}" stroke="#e3e8f2"/><text x="${P.l - 8}" y="${y + 4}" text-anchor="end">${short(v)}</text>`; }
  const step = Math.max(1, Math.ceil(points.length / 10));
  const pts = [];
  points.forEach((p, i) => {
    const h = p.y / max * (H - P.t - P.b), x = P.l + i * bw;
    g += `<rect x="${x + bw * .15}" y="${H - P.b - h}" width="${Math.max(bw * .7, 1)}" height="${h}" rx="2" fill="${color}" opacity="${i === points.length - 1 ? 1 : .55}"/>`;
    if (i % step === 0) g += `<text x="${x + bw / 2}" y="${H - 8}" text-anchor="middle">${esc(fmtX(p.x))}</text>`;
    pts.push([x + bw / 2, H - P.b - h, p.x, p.label ?? fmt(p.y)]);
  });
  return `<svg class="chart" style="height:260px" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" data-pts='${esc(JSON.stringify(pts))}'>${g}</svg>`;
}
// tooltip
const tip = Object.assign(document.createElement("div"), { className: "tip", hidden: true });
document.body.append(tip);
document.addEventListener("mousemove", e => {
  const svg = e.target.closest?.("svg.chart");
  if (!svg) { tip.hidden = true; return; }
  const pts = JSON.parse(svg.dataset.pts || "[]"); if (!pts.length) return;
  const r = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal, x = (e.clientX - r.left) / r.width * vb.width;
  let best = pts[0]; for (const p of pts) if (Math.abs(p[0] - x) < Math.abs(best[0] - x)) best = p;
  tip.hidden = false; tip.textContent = `${best[2]} · ${best[3]}`;
  tip.style.left = Math.min(e.clientX + 12, innerWidth - tip.offsetWidth - 8) + "px"; tip.style.top = e.clientY - 34 + "px";
  const c = svg.querySelector(".hov"); if (c) { c.style.display = ""; c.setAttribute("cx", best[0]); c.setAttribute("cy", best[1]); }
});


const GOV = [
  { short: "NAPP", ru: "Национальное агентство перспективных проектов", en: "National Agency of Perspective Projects", url: "https://napp.uz", c: "#b08d2e" },
  { short: "my.gov.uz", ru: "Единый портал интерактивных госуслуг", en: "Single portal of public services", url: "https://my.gov.uz", c: "#1d8fe1" },
  { short: "gov.uz", ru: "Правительственный портал Республики Узбекистан", en: "Government portal of Uzbekistan", url: "https://gov.uz", c: "#1a9a4b" },
  { short: "UzSAMA", ru: "Агентство по управлению государственными активами", en: "State Assets Management Agency", url: "https://davaktiv.uz", c: "#3b4a9c" },
  { short: "CSD", ru: "Центральный депозитарий ценных бумаг", en: "Central Securities Depository", url: "https://deponet.uz", c: "#1239a6" },
  { short: "LexUZ", ru: "Национальная база данных законодательства", en: "National legislation database", url: "https://lex.uz", c: "#1b6fc2" },
];
const govSection = () => sec(t("gov.title"), `<div class="gov">${GOV.map(g => `<a class="gov-card" href="${g.url}" target="_blank" rel="noopener" title="${esc(tl(g))}">
  <b style="color:${g.c}">${esc(g.short)}</b><small>${esc(tl(g))}</small></a>`).join("")}</div>`);

// ---------------- pages ----------------
const sec = (title, body, more) => `<section class="sec"><div class="sec-h"><h2>${title}</h2>${more ? `<a class="more" href="${more}">${t("more")} <span>⟶</span></a>` : ""}</div>${body}</section>`;

function tradesTable(rows) {
  return `<div class="card tbl-wrap"><table><thead><tr>
    <th>${t("th.time")}</th><th>${t("th.code")}</th><th>${t("th.logo")}</th><th>${t("th.issuer")}</th><th>${t("th.type")}</th>
    <th>${t("th.market")}</th><th>${t("th.board")}</th><th class="r">${t("th.price")}</th><th class="r">${t("th.qty")}</th><th class="r">${t("th.volume")}</th>
  </tr></thead><tbody>${rows.map(r => `<tr class="clk" data-href="#/stock/${esc(r.ticker)}">
    <td class="num">${dmy(r.trade_time)}<br><small class="muted">${r.trade_time.slice(11)}</small></td>
    <td class="t-code"><b>${esc(r.ticker)}</b><small>${esc(r.isin)}</small></td>
    <td><div class="logo-chip">${ini(r.issuer)}</div></td>
    <td>${esc(r.issuer)}</td><td><span class="type">${typeName(r.sec_type)}</span></td>
    <td>${esc(r.market)}</td><td>${esc(r.board)}</td>
    <td class="r num">${fmt(r.price)}</td><td class="r num">${fmt(r.quantity)}</td><td class="r num">${fmt(r.volume)} ${esc(r.currency)}</td>
  </tr>`).join("")}</tbody></table></div>`;
}

function liqWidget(l) {
  const p = k => l.total ? (l[k] / l.total * 100) : 0;
  return `<div class="card pad">
    <div class="liq-head"><span>${t("liq.asof", { m: monthName(l.as_of), n: l.total })}</span><a class="liq-arrow" href="#/stocks?liq=high">→</a></div>
    <div class="liq-bar"><i style="width:${p("high")}%;background:var(--high)"></i><i style="width:${p("mid")}%;background:var(--mid)"></i><i style="width:${p("low")}%;background:var(--low)"></i></div>
    <div class="liq-legend">
      <a href="#/stocks?liq=high" style="--c:var(--high);color:inherit"><b>${l.high}</b><small>${t("liq.high")}</small></a>
      <a href="#/stocks?liq=mid" style="--c:var(--mid);color:inherit"><b>${l.mid}</b><small>${t("liq.mid")}</small></a>
      <a href="#/stocks?liq=low" style="--c:var(--low);color:inherit"><b>${l.low}</b><small>${t("liq.low")}</small></a>
    </div>
    <div class="liq-top-h">${t("liq.top")}</div>
    <div class="liq-top">${l.top.map(x => `<a class="liq-pill" href="#/stock/${x.ticker}">${x.ticker} ${liqBadge(x.months)}</a>`).join("")}</div>
  </div>`;
}
function monthName(ym) {
  if (!ym) return "—";
  const [y, m] = ym.split("-");
  return new Date(+y, +m - 1, 1).toLocaleString(LANG === "ru" ? "ru-RU" : "en-US", { month: "long", year: "numeric" }).replace(/^./, c => c.toUpperCase()).replace(" г.", "");
}

async function pageHome() {
  const [ov, tr, liq, lst, note] = await Promise.all([
    cached("ov", () => api("/api/market/overview")), api("/api/stocks/trades?limit=10"),
    cached("liq", () => api("/api/stocks/liquidity")), cached("lst", () => api("/api/stocks/listings")), demoNote()]);
  const usd = `<div class="hs"><small>${t("st.usd")}</small><b class="num">${fmt(USD_TODAY.rate, 2)}</b><span>${dmy(USD_TODAY.date)}${ov.usd ? ` · ${t("st.usdData")}: ${fmt(ov.usd.rate, 2)} (${dmy(ov.usd.date)})` : ""}</span></div>`;
  const months = ov.monthly.slice(-24);
  return note + `
  <div class="hero">
    <div>
      <h1>${t("hero.title")}</h1><p>${t("hero.text")}</p>
      <form class="ask-box" id="heroAsk"><input name="q" placeholder="${t("hero.ph")}" autocomplete="off"><button class="btn">${t("hero.ask")}</button></form>
      <div class="chips">${EXAMPLES.slice(0, 4).map(([l, q]) => `<button class="chip" data-q="${esc(q)}">${l} · ${esc(q.length > 48 ? q.slice(0, 46) + "…" : q)}</button>`).join("")}</div>
    </div>
    <div class="hero-stats">
      <div class="hs"><small>${t("st.day")}</small><b class="num">${short(ov.day_turnover)}</b><span>${t("st.daydeals", { n: fmt(ov.day_deals), d: dmy(ov.last_date) })}</span></div>
      <div class="hs"><small>${t("st.month")}</small><b class="num">${short(ov.month_turnover)}</b><span>${t("st.monthdeals", { n: fmt(ov.month_deals) })} · ${monthName(ov.last_date.slice(0, 7))}</span></div>
      <div class="hs"><small>${t("st.deals")}</small><b class="num">${fmt(ov.total_deals)}</b><span>${dmy(ov.date_from)} — ${dmy(ov.date_to)}</span></div>
      ${usd}
    </div>
  </div>
  ${sec(t("sec.trades"), tradesTable(tr), "#/stocks")}
  ${sec(t("sec.liq"), liqWidget(liq), "#/stocks")}
  <div class="grid g2">
    ${sec(t("sec.monthly"), `<div class="card pad">${barChart(months.map(m => ({ x: m.month, y: m.turnover, label: short(m.turnover) + " · " + fmt(m.deals) + " " + t("th.deals").toLowerCase() })), { fmtX: x => x.slice(2).replace("-", ".") })}</div>`, "#/deals")}
    ${sec(t("sec.cats"), `<div class="card tbl-wrap"><table><thead><tr><th>${t("th.category")}</th><th class="r">${t("th.deals")}</th><th class="r">${t("th.turnover")}</th></tr></thead><tbody>
      ${ov.categories.map(c => `<tr class="clk" data-href="#/deals?category=${encodeURIComponent(c.category)}"><td>${esc(c.category)}</td><td class="r num">${fmt(c.deals)}</td><td class="r num">${short(c.turnover)}</td></tr>`).join("")}
    </tbody></table></div>`)}
  </div>
  ${sec(t("sec.listings"), `<div class="card tbl-wrap"><table><thead><tr><th>${t("th.logo")}</th><th>${t("th.ticker")}</th><th>${t("th.issuer")}</th><th>${t("th.listed")}</th><th>${t("th.currency")}</th><th class="r">${t("th.nominal")}</th><th class="r">${t("th.count")}</th></tr></thead><tbody>
    ${lst.slice(0, 6).map(r => `<tr class="clk" data-href="#/stock/${esc(r.ticker)}"><td><div class="logo-chip">${ini(r.issuer || r.ticker)}</div></td><td><b>${esc(r.ticker)}</b></td><td>${esc(r.issuer)}</td><td class="num">${dmy(r.listed_date)}</td><td>${r.currency}</td><td class="r num">${fmt(r.nominal)}</td><td class="r num">${fmt(r.shares)}</td></tr>`).join("")}
  </tbody></table></div>`, "#/listing")}
  ${govSection()}`;
}
function afterHome() {
  $("#heroAsk").onsubmit = e => { e.preventDefault(); const q = e.target.q.value.trim(); if (q) goAsk(q); };
}
function goAsk(q) { sessionStorage.setItem("pendingQ", q); location.hash = "#/agent"; }
document.addEventListener("click", e => {
  const c = e.target.closest("[data-q]"); if (c) { e.preventDefault(); goAsk(c.dataset.q); return; }
  const r = e.target.closest("tr[data-href]"); if (r && !e.target.closest("a,button")) location.hash = r.dataset.href;
});

// stocks
async function pageStocks(params) {
  const rows = await cached("stocks", () => api("/api/stocks"));
  const liq = params.get("liq") || "";
  return `<div class="page-h"><h1>${t("stocks.title")}</h1><p>${t("stocks.text")}</p></div>${await demoNote()}
  <div class="card">
    <div class="filters">
      <label>${t("th.ticker")}<input type="search" id="stQ" placeholder="${t("stocks.search")}"></label>
      <label>${t("th.liq")}<div class="seg" id="stLiq">${["", "high", "mid", "low"].map(k => `<button data-v="${k}" class="${k === liq ? "on" : ""}">${k ? t("liq." + k) : t("all")}</button>`).join("")}</div></label>
    </div>
    <div class="tbl-wrap"><table><thead><tr><th></th><th>${t("th.ticker")}</th><th>${t("th.issuer")}</th><th>${t("th.type")}</th>
      <th class="r">${t("th.last")}</th><th class="r">${t("th.chg")}</th><th class="r">${t("th.close")}</th><th class="r">${t("th.dayvol")}</th><th class="r">${t("th.liq")}</th></tr></thead>
      <tbody id="stBody"></tbody></table></div>
  </div>`;
}
function afterStocks(params) {
  const rows = cache.stocks; let liq = params.get("liq") || "";
  const draw = async () => {
    const all = await rows, q = $("#stQ").value.trim().toLowerCase();
    const f = all.filter(s => (!liq || s.liquidity === liq) && (!q || s.ticker.toLowerCase().includes(q) || s.issuer.toLowerCase().includes(q)));
    $("#stBody").innerHTML = f.map(s => `<tr class="clk" data-href="#/stock/${s.ticker}">
      <td>${starBtn("stock", s.ticker)}</td>
      <td class="t-code"><b>${esc(s.ticker)}</b><small>${esc(s.isin || "")}</small></td><td>${esc(s.issuer)}</td><td><span class="type">${typeName(s.sec_type)}</span></td>
      <td class="r num">${fmt(s.price)} <small class="muted">${s.currency}</small></td>
      <td class="r num ${cls(s.change)}">${sign(s.change)}${fmt(s.change)} (${sign(s.change)}${fmt(s.change_pct, 2)}%)</td>
      <td class="r num">${fmt(s.close)}</td><td class="r num">${fmt(s.day_volume)}</td>
      <td class="r">${liqBadge(s.months)}</td></tr>`).join("") || `<tr><td colspan="10" class="empty">—</td></tr>`;
  };
  $("#stQ").oninput = draw;
  $("#stLiq").onclick = e => { const b = e.target.closest("button"); if (!b) return; liq = b.dataset.v; $("#stLiq").querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b)); draw(); };
  draw();
}

async function pageStock(tk) {
  const s = await api("/api/stocks/" + encodeURIComponent(tk));
  return `<a href="#/stocks" class="muted">${t("back")}</a>
  <div class="card pad" style="margin:14px 0 18px"><div class="dt-head">
    <div class="logo-chip">${ini(s.issuer)}</div>
    <div><h1>${s.ticker}</h1><div class="muted">${esc(s.issuer)} · <span class="type">${typeName(s.sec_type)}</span></div></div>
    <div class="dt-price"><b class="num">${fmt(s.price)} <small class="muted" style="font-size:15px">${s.currency}</small></b>
      <span class="num ${cls(s.change)}">${sign(s.change)}${fmt(s.change)} (${sign(s.change)}${fmt(s.change_pct, 2)}%) · ${dmy(s.last_day)}</span></div>
  </div>
  <div style="display:flex;gap:10px;margin-top:16px;flex-wrap:wrap">
    <button class="btn ghost sm star-btn" data-watch="stock:${s.ticker}" data-label="1">${isWatched("stock", s.ticker) ? "★ " + t("dt.watched") : "☆ " + t("dt.watch")}</button>
    <button class="btn sm" data-q="${esc(LANG === "ru" ? `Какая цена акций ${s.ticker}?` : `What is the price of ${s.ticker} shares?`)}">${t("dt.ask")}</button>
  </div></div>
  <div class="grid g2">
    <div class="card pad"><h3 style="margin:0 0 10px">${s.real ? t("dt.daytrades") : t("dt.chart")}</h3>${s.series.length > 1 ? lineChart(s.series.map(p => ({ x: s.real ? p.day.slice(11) : dmy(p.day), y: p.close })), { fmtY: v => fmt(v, v < 100 ? 2 : 0) }) : `<div class="empty">—</div>`}</div>
    <div class="card pad"><div class="kv" style="grid-template-columns:1fr 1fr">
      ${s.real ? `
      <div><small>${t("th.close")}</small><b class="num">${fmt(s.close)} ${esc(s.currency)}</b></div><div><small>${t("th.last")}</small><b class="num">${fmt(s.price)} ${esc(s.currency)}</b></div>
      <div><small>${t("th.chg")}</small><b class="num ${cls(s.change)}">${sign(s.change)}${fmt(s.change)}</b></div><div><small>${t("dt.qdate")}</small><b>${dmy(s.last_day)}</b></div>
      <div><small>${t("dt.isin")}</small><b>${esc(s.isin || "—")}</b></div><div><small>${t("dt.ntrades")}</small><b class="num">${fmt(s.day_trades)}</b></div>
      <div><small>${t("th.dayvol")}</small><b class="num">${fmt(s.day_volume)}</b></div><div><small>${t("dt.liq")}</small><b>${liqBadge(s.months)}</b></div>
      <div style="grid-column:1/-1"><small>${t("dt.source")}</small><b>${esc(s.source)}</b></div>` : `
      <div><small>${t("dt.isin")}</small><b>${esc(s.isin)}</b></div><div><small>${t("dt.listed")}</small><b>${dmy(s.listed_date)}</b></div>
      <div><small>${t("dt.nominal")}</small><b class="num">${fmt(s.nominal)} ${s.currency}</b></div><div><small>${t("dt.shares")}</small><b class="num">${fmt(s.shares)}</b></div>
      <div><small>${t("dt.cap")}</small><b class="num">${short(s.cap)} ${s.currency}</b></div><div><small>${t("th.vol30")}</small><b class="num">${short(s.vol_30d)}</b></div>
      <div><small>${t("th.dayvol")}</small><b class="num">${fmt(s.day_volume)}</b></div><div><small>${t("dt.liq")}</small><b>${liqBadge(s.months)}</b></div>`}
    </div></div>
  </div>
  ${sec(t("dt.trades"), `<div class="card tbl-wrap"><table><thead><tr><th>${t("th.time")}</th><th class="r">${t("th.price")}</th><th class="r">${t("th.qty")}</th><th class="r">${t("th.volume")}</th></tr></thead><tbody>
    ${s.trades.map(r => `<tr><td class="num">${dmy(r.trade_time)} ${r.trade_time.slice(11)}</td><td class="r num">${fmt(r.price)}</td><td class="r num">${fmt(r.quantity)}</td><td class="r num">${fmt(r.volume)} ${esc(r.currency)}</td></tr>`).join("")}
  </tbody></table></div>`)}`;
}

// commodities
async function pageCommodities() {
  const rows = await cached("ticker", () => api("/api/market/ticker"));
  return `<div class="page-h"><h1>${t("com.title")}</h1><p>${t("com.text")}</p></div>${await demoNote(true)}
  <div class="card tbl-wrap"><table><thead><tr><th></th><th>${t("th.product")}</th><th>${t("th.date")}</th><th class="r">${t("th.vwap")}</th><th class="r">${t("th.chg")}</th><th class="r">${t("th.turnover")}</th></tr></thead><tbody>
  ${rows.map(x => `<tr class="clk" data-href="#/commodity/${encodeURIComponent(x.code)}"><td>${starBtn("commodity", x.code)}</td>
    <td class="t-code"><b>${esc(x.name)}</b><small>${esc(x.category || x.code)}</small></td><td class="num">${dmy(x.date)}</td>
    <td class="r num">${fmt(x.price, 2)}</td><td class="r num ${cls(x.change)}">${sign(x.change)}${fmt(x.change, 2)} (${fmt(Math.abs(x.change_pct), 2)}%)</td>
    <td class="r num">${short(x.turnover)}</td></tr>`).join("")}
  </tbody></table></div>`;
}

async function pageCommodity(code) {
  const c = await api("/api/commodity/" + encodeURIComponent(code));
  if (c.quote) {
    const q = c.quote;
    return `<a href="#/commodities" class="muted">${t("back")}</a>
    <div class="card pad" style="margin:14px 0 18px"><div class="dt-head">
      <div class="logo-chip">${ini(c.name)}</div>
      <div><h1>${esc(c.name)}</h1><div class="muted">${esc(c.category)} · ${t("dt.quote")}</div></div>
      <div class="dt-price"><b class="num">${fmt(q.price, 2)} <small class="muted" style="font-size:15px">${esc(q.currency)}</small></b>
        <span class="num ${cls(q.change)}">${sign(q.change)}${fmt(q.change, 2)} (${sign(q.change)}${fmt(q.change_pct, 2)}%) · ${dmy(q.date)}</span></div>
    </div>
    <div style="display:flex;gap:10px;margin-top:16px;flex-wrap:wrap">
      <button class="btn ghost sm" data-watch="commodity:${esc(c.code)}" data-label="1">${isWatched("commodity", c.code) ? "★ " + t("dt.watched") : "☆ " + t("dt.watch")}</button>
      ${c.registry_query ? `<a class="btn ghost sm" href="#/deals?q=${encodeURIComponent(c.registry_query)}">${t("dt.reg", { n: fmt(c.registry_deals) })}</a>` : ""}
      <button class="btn sm" data-q="${esc(LANG === "ru" ? `Какая котировка «${c.name}»?` : `What is the quote for "${c.name}"?`)}">${t("dt.ask")}</button>
    </div>
    <div class="kv" style="margin-top:20px">
      <div><small>${t("th.vwap")}</small><b class="num">${fmt(q.price, 2)}</b></div>
      <div><small>${t("th.chg")}</small><b class="num ${cls(q.change)}">${sign(q.change)}${fmt(q.change, 2)} (${fmt(q.change_pct, 2)}%)</b></div>
      <div><small>${t("dt.qdate")}</small><b>${dmy(q.date)}</b></div>
      <div><small>${t("dt.source")}</small><b>${esc(q.source)}</b></div>
    </div>${c.registry_query ? "" : `<p class="muted" style="margin:18px 0 0">${t("dt.noreg")}</p>`}</div>`;
  }
  return `<a href="#/commodities" class="muted">${t("back")}</a>
  <div class="card pad" style="margin:14px 0 18px"><div class="dt-head">
    <div class="logo-chip">${ini(c.name)}</div>
    <div><h1>${esc(c.name)}</h1><div class="muted">${esc(c.code)} · ${esc(c.category)} · ${esc(c.unit)}</div></div>
    <div style="margin-left:auto;display:flex;gap:10px;flex-wrap:wrap">
      <button class="btn ghost sm" data-watch="commodity:${esc(c.code)}" data-label="1">${isWatched("commodity", c.code) ? "★ " + t("dt.watched") : "☆ " + t("dt.watch")}</button>
      <a class="btn ghost sm" href="#/deals?instrument=${encodeURIComponent(c.code)}">${t("nav.deals")}</a>
      <button class="btn sm" data-q="${esc(LANG === "ru" ? `Как менялась средняя цена товара «${c.name}» по месяцам в 2026 году?` : `How did the average price of "${c.name}" change by month in 2026?`)}">${t("dt.ask")}</button>
    </div></div>
    <div class="kv" style="margin-top:20px">
      <div><small>${t("th.deals")}</small><b class="num">${fmt(c.deals)}</b></div>
      <div><small>${t("th.turnover")}</small><b class="num">${short(c.turnover)} UZS</b></div>
      <div><small>${t("dt.totq")}</small><b class="num">${fmt(c.quantity)} ${esc(c.unit)}</b></div>
      <div><small>${t("dt.period")}</small><b>${dmy(c.date_from)} — ${dmy(c.date_to)}</b></div>
    </div></div>
  <div class="grid g2">
    <div class="card pad"><h3 style="margin:0 0 10px">${t("dt.cchart")}</h3>${lineChart(c.series.map(p => ({ x: p.month, y: p.vwap })), { fmtX: x => x.slice(2).replace("-", ".") })}</div>
    <div class="card tbl-wrap"><table><thead><tr><th>${t("dt.buyers")}</th><th class="r">${t("th.deals")}</th><th class="r">${t("th.turnover")}</th></tr></thead><tbody>
      ${c.top_buyers.map(b => `<tr><td>${esc(b.buyer)}</td><td class="r num">${fmt(b.deals)}</td><td class="r num">${short(b.turnover)}</td></tr>`).join("")}</tbody></table></div>
  </div>
  ${sec(t("dt.monthly"), `<div class="card tbl-wrap"><table><thead><tr><th>${t("th.month")}</th><th class="r">${t("th.vwap")}</th><th class="r">${t("th.low")}</th><th class="r">${t("th.high")}</th><th class="r">${t("th.qty")}</th><th class="r">${t("th.deals")}</th><th class="r">${t("th.turnover")}</th></tr></thead><tbody>
    ${c.series.slice().reverse().slice(0, 18).map(m => `<tr><td>${monthName(m.month)}</td><td class="r num">${fmt(m.vwap, 2)}</td><td class="r num">${fmt(m.low)}</td><td class="r num">${fmt(m.high)}</td><td class="r num">${fmt(m.qty)}</td><td class="r num">${fmt(m.deals)}</td><td class="r num">${short(m.turnover)}</td></tr>`).join("")}
  </tbody></table></div>`)}`;
}

// deals registry
async function pageDeals(params) {
  const fc = await cached("facets", () => api("/api/deals/facets"));
  const opt = (arr, v) => `<option value="">${t("all")}</option>` + arr.map(x => typeof x === "string" ? `<option ${x === v ? "selected" : ""}>${esc(x)}</option>` : `<option value="${esc(x.code)}" ${x.code === v ? "selected" : ""}>${esc(x.name)}</option>`).join("");
  return `<div class="page-h"><h1>${t("deals.title")}</h1><p>${t("deals.text")}</p></div>${await demoNote(true)}
  <div class="card">
    <form class="filters" id="dlF">
      <label>${t("f.search")}<input type="search" name="q" value="${esc(params.get("q") || "")}"></label>
      <label>${t("f.from")}<input type="date" name="date_from" value="${esc(params.get("date_from") || "")}"></label>
      <label>${t("f.to")}<input type="date" name="date_to" value="${esc(params.get("date_to") || "")}"></label>
      <label>${t("f.product")}<select name="instrument">${opt(fc.instrument, params.get("instrument"))}</select></label>
      <label>${t("f.category")}<select name="category">${opt(fc.category, params.get("category"))}</select></label>
      <label>${t("f.region")}<select name="region">${opt(fc.region, params.get("region"))}</select></label>
      ${fc.status && fc.status.length ? `<label>${t("f.status")}<select name="status">${opt(fc.status, params.get("status"))}</select></label>` : ""}
      ${fc.contract_form && fc.contract_form.length ? `<label>${t("f.form")}<select name="contract_form">${opt(fc.contract_form, params.get("contract_form"))}</select></label>` : ""}
      ${fc.market && fc.market.length > 1 ? `<label>${t("f.market")}<select name="market">${opt(fc.market, params.get("market"))}</select></label>` : ""}
      <button type="button" class="btn ghost" id="dlReset">${t("f.reset")}</button>
      <button type="button" class="btn ghost" id="dlCsv">${t("f.csv")}</button>
    </form>
    <div class="tbl-wrap"><table class="wide"><thead><tr>
      <th class="sortable" data-s="deal_id">${t("th.deal")}</th><th class="sortable" data-s="deal_date">${t("th.date")}</th><th class="sortable" data-s="instrument_name">${t("th.product")}</th>
      <th>${t("th.section")}</th><th>${t("th.status")}</th><th class="r sortable" data-s="quantity">${t("th.qty")}</th><th class="r sortable" data-s="price">${t("th.price")}</th><th class="r sortable" data-s="amount">${t("th.amount")}</th>
      <th>${t("th.seller")}</th><th>${t("th.buyer")}</th><th>${t("th.region")}</th><th>${t("th.brokers")}</th><th>${t("th.source")}</th>
    </tr></thead><tbody id="dlBody"><tr><td colspan="13" class="skel">${t("loading")}</td></tr></tbody></table></div>
    <div class="pager"><span id="dlInfo"></span><div class="btns"><button class="btn ghost sm" id="dlPrev">${t("prev")}</button><span id="dlPage" style="align-self:center;padding:0 8px"></span><button class="btn ghost sm" id="dlNext">${t("next")}</button></div></div>
  </div>`;
}
function afterDeals() {
  let page = 1, sort = "deal_date", order = "desc", last = null;
  const form = $("#dlF");
  const qs = () => { const p = new URLSearchParams(); for (const [k, v] of new FormData(form)) if (v) p.set(k, v); return p; };
  const load = async () => {
    const p = qs(); p.set("page", page); p.set("size", 50); p.set("sort", sort); p.set("order", order);
    const d = last = await api("/api/deals?" + p);
    const pages = Math.max(1, Math.ceil(d.total / d.size));
    $("#dlInfo").textContent = t("pager", { n: fmt(d.total), s: short(d.sum_amount) + " UZS" });
    $("#dlPage").textContent = t("page", { p: page, t: fmt(pages) });
    $("#dlPrev").disabled = page <= 1; $("#dlNext").disabled = page >= pages;
    $("#dlBody").innerHTML = d.rows.map(r => `<tr>
      <td class="num"><b>${esc(r.deal_id)}</b></td><td class="num">${dmy(r.deal_date)}${r.deal_time ? `<br><small class="muted">${esc(r.deal_time)}</small>` : ""}</td>
      <td><a href="#/commodity/${encodeURIComponent(r.instrument)}">${esc(r.instrument_name)}</a><br><small class="muted">${esc(r.product_name && r.product_name !== r.instrument_name ? r.product_name : r.category)}</small></td>
      <td>${esc(r.market)}${r.contract_form ? `<br><small class="muted">${esc(r.contract_form)}${r.trade_type ? " · " + esc(r.trade_type) : ""}</small>` : ""}</td>
      <td><span class="st ${/Аннулир/.test(r.status || "") ? "bad" : /Исполнен/.test(r.status || "") ? "ok" : ""}">${esc(r.status || "—")}</span></td>
      <td class="r num">${fmt(r.quantity)} ${esc(r.unit || "")}</td><td class="r num">${fmt(r.price)}</td>
      <td class="r num"><b>${fmt(r.amount)}</b> ${esc(r.currency || "")}${r.currency === "USD" && r.amount_uzs ? `<br><small class="muted">≈ ${short(r.amount_uzs)} UZS</small>` : ""}</td>
      <td>${esc(r.seller)}${r.seller_inn ? `<br><small class="muted">${esc(r.seller_inn)}</small>` : ""}</td><td>${esc(r.buyer)}${r.buyer_inn ? `<br><small class="muted">${esc(r.buyer_inn)}</small>` : ""}</td><td>${esc(r.region)}</td>
      <td><small>${esc(r.seller_broker || "—")}<br>${esc(r.buyer_broker || "—")}</small></td>
      <td><small class="muted">${esc(r.source_file)}:${r.source_row}</small></td></tr>`).join("") || `<tr><td colspan="13" class="empty">—</td></tr>`;
    history.replaceState(null, "", "#/deals?" + qs());
  };
  form.oninput = form.onchange = () => { page = 1; clearTimeout(form._t); form._t = setTimeout(load, 250); };
  form.onsubmit = e => e.preventDefault();
  $("#dlReset").onclick = () => { form.querySelectorAll("input,select").forEach(i => i.value = ""); page = 1; load(); };
  $("#dlPrev").onclick = () => { page--; load(); };
  $("#dlNext").onclick = () => { page++; load(); };
  document.querySelectorAll("th.sortable").forEach(th => th.onclick = () => {
    if (sort === th.dataset.s) order = order === "desc" ? "asc" : "desc"; else { sort = th.dataset.s; order = "desc"; }
    page = 1; load();
  });
  $("#dlCsv").onclick = () => {
    if (!last) return;
    const cols = Object.keys(last.rows[0] || {});
    const csv = [cols.join(","), ...last.rows.map(r => cols.map(c => `"${String(r[c] ?? "").replace(/"/g, '""')}"`).join(","))].join("\n");
    const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(new Blob(["﻿" + csv], { type: "text/csv" })), download: `deals_page${page}.csv` });
    a.click(); URL.revokeObjectURL(a.href);
  };
  load();
}

// participants
async function pageParticipants(params) {
  const q = params?.get("q") || "", role = params?.get("role") || "", page = +(params?.get("page") || 1);
  const sp = new URLSearchParams({ q, role, page, size: 50 });
  const [br, pt] = await Promise.all([api("/api/brokers"), api("/api/participants/search?" + sp)]);
  const pages = Math.max(1, Math.ceil(pt.total / pt.size));
  const link = (pg) => { const x = new URLSearchParams(); if (q) x.set("q", q); if (role) x.set("role", role); if (pg > 1) x.set("page", pg); const s = x.toString(); return "#/participants" + (s ? "?" + s : ""); };
  const ru = LANG === "ru";
  const form = `<form class="filters" id="ptForm" style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
    <input name="q" value="${esc(q)}" placeholder="${ru ? "Название или ИНН" : "Name or INN"}" style="flex:1;min-width:180px">
    <select name="role"><option value="">${ru ? "Все роли" : "All roles"}</option>
      <option value="seller"${role === "seller" ? " selected" : ""}>${t("role.seller")}</option>
      <option value="buyer"${role === "buyer" ? " selected" : ""}>${t("role.buyer")}</option></select>
    <button class="btn sm">${ru ? "Найти" : "Search"}</button></form>`;
  const pager = `<div style="display:flex;gap:8px;align-items:center;justify-content:space-between;margin-top:8px">
    <small class="muted">${ru ? "Найдено" : "Found"}: ${fmt(pt.total)} · ${ru ? "стр." : "page"} ${fmt(pt.page)} / ${fmt(pages)}</small>
    <span>${pt.page > 1 ? `<a class="btn ghost sm" href="${link(pt.page - 1)}">←</a>` : ""} ${pt.page < pages ? `<a class="btn ghost sm" href="${link(pt.page + 1)}">→</a>` : ""}</span></div>`;
  return `<div class="page-h"><h1>${t("part.title")}</h1><p>${t("part.text")}</p></div>${await demoNote(true)}
  <div class="grid g2">
    ${sec(t("part.list"), `${form}<div class="card tbl-wrap"><table><thead><tr><th>${t("th.name")}</th><th>${t("th.role")}</th><th>${t("th.region")}</th><th>${t("th.inn")}</th></tr></thead><tbody>
      ${pt.rows.map(p => `<tr class="clk" data-href="#/deals?q=${encodeURIComponent(p.inn)}"><td>${esc(p.name)}</td><td>${t("role." + p.role)}</td><td>${esc(p.region)}</td><td class="num">${esc(p.inn)}</td></tr>`).join("")}</tbody></table></div>${pager}`)}
    ${sec(t("part.brokers"), `<div class="card tbl-wrap"><table><thead><tr><th>${t("th.code")}</th><th>${t("th.name")}</th><th>${t("th.inn")}</th><th>${t("th.region")}</th></tr></thead><tbody>
      ${br.map(b => `<tr><td><b>${esc(b.code)}</b></td><td>${esc(b.name)}</td><td>${esc(b.inn ?? "")}</td><td>${esc(b.region ?? "")}</td></tr>`).join("")}</tbody></table></div>`)}
  </div>`;
}
function afterParticipants() {
  $("#ptForm")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const x = new URLSearchParams(); for (const [k, v] of new FormData(e.target)) if (v) x.set(k, v);
    location.hash = "#/participants" + (x.toString() ? "?" + x : "");
  });
}

// AI agent
function mdLite(s) {
  return esc(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/^#{1,4}\s*(.+)$/gm, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>");
}
function evTable(e) {
  return `<div class="tbl-wrap"><table><thead><tr>${e.columns.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>
    ${e.rows.map(r => `<tr>${r.map(v => `<td class="num">${typeof v === "number" ? fmt(v) : esc(v)}</td>`).join("")}</tr>`).join("")}</tbody></table>
    ${e.row_count > e.rows.length ? `<small class="muted">… ${fmt(e.rows.length)} / ${fmt(e.row_count)}${e.truncated ? "+" : ""}</small>` : ""}</div>`;
}
function answerHtml(m) {
  if (m.pending) return `<div class="msg a"><span class="dots">${t("ag.thinking")}</span></div>`;
  if (m.error) return `<div class="msg a"><div class="body down">${t("ag.err")}${esc(m.error)}</div></div>`;
  const d = m.data;
  return `<div class="msg a"><div class="body">${mdLite(d.answer)}</div>
    <div class="verify ${d.verified ? "ok" : "no"}">${d.verified ? "✓ " + t("ag.ok") : "⚠ " + t("ag.no") + esc(d.unsupported.join(", "))}</div>
    <div class="meta-line">${t("ag.time", { s: fmt(d.seconds, 1) })} · ${t("ag.engine." + (d.engine || "claude"))}${d.note ? " · " + esc(d.note) : ""}</div>
    ${d.queries.length ? `<details class="ev"><summary>${t("ag.sql", { n: d.queries.length })}</summary>${d.queries.map(q => `<pre>${esc(q)}</pre>`).join("")}</details>` : ""}
    ${d.evidence?.length ? `<details class="ev" open><summary>${t("ag.ev")}</summary>${d.evidence.map(evTable).join("")}</details>` : ""}
  </div>`;
}
function chatHtml() {
  return `<div class="msg a"><div class="body">${t("ag.hello")}</div></div>` +
    S.chat.map(m => `<div class="msg q">${esc(m.q)}</div>${answerHtml(m)}`).join("");
}
async function pageAgent() {
  return `<div class="page-h"><h1>${t("ag.title")}</h1><p>${t("ag.text")}</p></div>${await demoNote(true)}
  <div class="agent">
    <div class="card chat">
      <div class="chat-log" id="log">${chatHtml()}</div>
      <form class="chat-in" id="askF"><textarea name="q" placeholder="${t("ag.ph")}" rows="1"></textarea><button class="btn">${t("ag.send")}</button></form>
    </div>
    <aside class="side">
      <div class="card pad" style="margin-bottom:16px"><h3>${t("ag.examples")}</h3>
        ${EXAMPLES.map(([l, q]) => `<button class="ex" data-ask="${esc(q)}"><small>${l}</small>${esc(q)}</button>`).join("")}
        <button class="btn ghost sm" id="clearChat" style="margin-top:6px">${t("ag.clear")}</button>
      </div>
      <div class="card pad"><h3>${t("ag.rules")}</h3><ul class="rules" style="padding-left:18px;margin:0">${[1, 2, 3, 4, 5].map(i => `<li>${t("ag.r" + i)}</li>`).join("")}</ul></div>
    </aside>
  </div>`;
}
function afterAgent() {
  const f = $("#askF"), ta = f.q;
  const redraw = () => { $("#log").innerHTML = chatHtml(); const last = $("#log").lastElementChild; last?.scrollIntoView({ block: "nearest", behavior: "smooth" }); };
  const send = async q => {
    q = q.trim(); if (!q) return;
    const history = S.chat.filter(m => m.data).slice(-3).map(m => ({ q: m.q, a: m.data.answer }));
    const m = { q, pending: true }; S.chat.push(m); redraw();
    try { m.data = await api("/api/ask", { method: "POST", json: { question: q, history } }); }
    catch (e) { m.error = e.message; }
    m.pending = false;
    if (location.hash.startsWith("#/agent")) redraw();
  };
  f.onsubmit = e => { e.preventDefault(); const q = ta.value; ta.value = ""; send(q); };
  ta.onkeydown = e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); f.requestSubmit(); } };
  document.querySelectorAll("[data-ask]").forEach(b => b.onclick = () => send(b.dataset.ask));
  $("#clearChat").onclick = () => { S.chat = []; redraw(); };
  const pending = sessionStorage.getItem("pendingQ");
  if (pending) { sessionStorage.removeItem("pendingQ"); send(pending); }
  ta.focus();
}

// cabinet
async function pageCabinet(params) {
  if (!S.user) {
    const tab = params.has("register") ? "register" : "login";
    return `<div class="page-h"><h1>${t("cab.title")}</h1></div>
    <div class="card pad auth-card">
      <div class="tabs"><button data-tab="login" class="${tab === "login" ? "on" : ""}">${t("auth.signin")}</button><button data-tab="register" class="${tab === "register" ? "on" : ""}">${t("auth.register")}</button></div>
      ${params.has("forgot") ? `<div class="demo-note">${t("auth.forgot.text")}</div>` : ""}
      <form id="authF" data-mode="${tab}">
        <label class="field">${t("auth.role")}<select name="role">${["investor", "broker", "participant"].map(r => `<option value="${r}">${t("role." + r)}</option>`).join("")}</select></label>
        <label class="field reg-only" ${tab === "login" ? "hidden" : ""}>${t("auth.name")}<input name="name" autocomplete="name"></label>
        <label class="field">${t("auth.login")}<input name="login" required autocomplete="username"></label>
        <label class="field">${t("auth.password")}<input name="password" type="password" required autocomplete="${tab === "login" ? "current-password" : "new-password"}"></label>
        <div class="form-err" hidden></div>
        <button class="btn-green" style="width:100%">${tab === "login" ? t("auth.signin") : t("auth.create")}</button>
      </form>
    </div>`;
  }
  const [hist, stocks, tick] = await Promise.all([api("/api/me/history"), cached("stocks", () => api("/api/stocks")), cached("ticker", () => api("/api/market/ticker"))]);
  const u = S.user;
  const wl = S.watch.map(w => {
    if (w.kind === "stock") { const s = stocks.find(x => x.ticker === w.code); return s && `<tr class="clk" data-href="#/stock/${s.ticker}"><td>${starBtn("stock", s.ticker)}</td><td><b>${s.ticker}</b><br><small class="muted">${esc(s.issuer)}</small></td><td class="r num">${fmt(s.price)}</td><td class="r num ${cls(s.change)}">${sign(s.change)}${fmt(s.change_pct, 2)}%</td></tr>`; }
    const c = tick.find(x => x.code === w.code); return c && `<tr class="clk" data-href="#/commodity/${encodeURIComponent(c.code)}"><td>${starBtn("commodity", c.code)}</td><td><b>${esc(c.name)}</b><br><small class="muted">${esc(c.code)}</small></td><td class="r num">${fmt(c.price, 2)}</td><td class="r num ${cls(c.change)}">${sign(c.change)}${fmt(c.change_pct, 2)}%</td></tr>`;
  }).filter(Boolean).join("");
  return `<div class="page-h"><h1>${t("cab.title")}</h1></div>
  <div class="card pad" style="margin-bottom:22px"><div class="profile">
    <div class="avatar">${esc(u.name.slice(0, 1).toUpperCase())}</div>
    <div style="flex:1"><b style="font-size:19px">${esc(u.name)}</b><div class="muted">@${esc(u.login)} · ${t("role." + u.role)} · ${t("cab.since", { d: dmy(u.created) })}</div></div>
    <button class="btn ghost" id="logout">${t("auth.logout")}</button>
  </div></div>
  <div class="grid g2">
    <div>${sec(t("cab.hist"), `<div class="card pad">${hist.length ? hist.map(h => `<div class="hist-item"><b>${esc(h.question)}</b><small class="muted">${h.created} · ${h.verified ? "✓" : "⚠"}</small><p>${esc(h.answer)}</p><button class="btn ghost sm" data-q="${esc(h.question)}" style="margin-top:6px">↻</button></div>`).join("") : `<div class="empty">${t("cab.nohist")}</div>`}</div>`)}</div>
    <div>
      ${sec(t("cab.watch"), `<div class="card tbl-wrap">${wl ? `<table><tbody>${wl}</tbody></table>` : `<div class="empty">${t("cab.nowatch")}</div>`}</div>`)}
      ${sec(t("cab.upload"), `<div class="card pad"><p class="muted" style="margin-top:0">${t("cab.upload.text")}</p><input type="file" id="upl" accept=".csv,.xlsx,.xls,.json,.html,.htm"><div id="uplMsg" style="margin-top:10px"></div></div>`)}
    </div>
  </div>`;
}
function afterCabinet() {
  const f = $("#authF");
  if (f) {
    document.querySelectorAll("[data-tab]").forEach(b => b.onclick = () => { location.hash = "#/cabinet" + (b.dataset.tab === "register" ? "?register" : ""); });
    f.onsubmit = async e => {
      e.preventDefault();
      const body = Object.fromEntries(new FormData(f)), err = $(".form-err", f);
      try {
        const d = await api("/api/auth/" + f.dataset.mode, { method: "POST", json: body });
        store("token", d.token); await loadMe(); applyI18n(); location.hash = "#/cabinet"; route();
      } catch (x) { err.hidden = false; err.textContent = t("auth.err." + (x.detail || "invalid")); }
    };
    return;
  }
  $("#logout").onclick = async () => { await api("/api/auth/logout", { method: "POST" }).catch(() => {}); store("token", null); await loadMe(); applyI18n(); route(); };
  $("#upl").onchange = async e => {
    const fd = new FormData(); fd.append("file", e.target.files[0]);
    try {
      const d = await api("/api/upload", { method: "POST", body: fd });
      $("#uplMsg").innerHTML = `<span class="up">✓ ${esc(t("cab.uploaded", { f: d.file, n: fmt(d.added) }))}</span>`;
      Object.keys(cache).forEach(k => delete cache[k]); renderTape(); footer();
    } catch (x) { $("#uplMsg").innerHTML = `<span class="down">${esc(x.message)}</span>`; }
  };
}

// about / solution description
async function pageAbout() {
  const d = await cached("data", () => api("/api/data"));
  const tables = Object.entries(d.other_tables || {}).map(([k, v]) => `<li><code>${k}</code> — ${fmt(v.rows)}</li>`).join("");
  const ru = LANG === "ru";
  const steps = ru
    ? [["1. Загрузка", "CSV/XLSX/JSON/HTML → единая схема, колонки на uz/ru/en сопоставляются автоматически"], ["2. SQLite", "Сделки + источник (файл, строка) для каждой записи; база только для чтения"], ["3. Claude + tools", "describe_data, distinct_values, run_sql (только один SELECT)"], ["4. Проверка", "Каждое число в ответе сверяется с результатами SQL; при расхождении — переписывание"], ["5. Ответ", "Текст + SQL + строки-источники + отметка проверки"]]
    : [["1. Ingest", "CSV/XLSX/JSON/HTML → one schema; uz/ru/en column names mapped automatically"], ["2. SQLite", "Deals + source (file, row) for every record; read-only for the agent"], ["3. Claude + tools", "describe_data, distinct_values, run_sql (single SELECT only)"], ["4. Verification", "Every number in the answer is matched against SQL results; mismatch → rewrite"], ["5. Answer", "Text + SQL + source rows + verification badge"]];
  return `<div class="page-h"><h1>${t("about.title")}</h1></div>
  <div class="card pad prose">
    <div class="flow">${steps.map(([h, p]) => `<div><b>${h}</b>${p}</div>`).join("")}</div>
    ${ru ? `
    <h3>Технологии</h3>
    <ul><li><b>Backend:</b> Python 3, FastAPI, SQLite, pandas (загрузка и нормализация файлов).</li>
      <li><b>LLM:</b> Claude (Anthropic API) с вызовом инструментов — модель не видит «сырые» данные целиком, а запрашивает их через SQL.</li>
      <li><b>Frontend:</b> HTML/CSS/JS без фреймворков, графики на SVG, языки RU/EN; агент понимает вопросы на RU/UZ/EN.</li>
      <li><b>Кабинет:</b> регистрация/вход (PBKDF2-хеши паролей, токены сессий), избранное, история вопросов, загрузка файлов.</li></ul>
    <h3>Подготовка данных (реестр uzex_spot_data)</h3>
    <ul><li>Каждая сделка связана с карточкой контракта: валюта, код ТН ВЭД, категория. Названия участников — по ИНН, брокеры — по коду.</li>
      <li>Один товар продавцы пишут по-разному («Мука», «МУКА ПШЕНИЧНАЯ…»), поэтому товар = код ТН ВЭД с единым названием (42 товара); исходное название сохранено. Мазут и дизель, бензин в литрах и в тоннах разделены.</li>
      <li>Объём = лоты × размер лота, цена = сумма ÷ объём; дизель из кг приведён к тоннам.</li>
      <li>USD-сделки пересчитаны в сумы по курсу на дату сделки (<code>amount_uzs</code>).</li>
      <li>Аннулированные (неоплаченные) сделки не входят в обороты, объёмы и цены; в количестве сделок показываются отдельно.</li></ul>
    <h3>Два режима агента</h3>
    <ul><li><b>Claude + SQL</b> — если задан API-ключ: любые свободные вопросы.</li>
      <li><b>Офлайн-движок</b> — без ключа или при ошибке API: распознаёт товар (RU/UZ/EN, падежи), период, условия (экспорт, спот/форвард/фьючерс, тип аукциона) и показатель (количество, сумма, топ-N, средняя цена и её динамика, доля аннулированных, статусы, сроки оплаты и поставки, оборот в USD) → готовый SQL. Если вопрос не понят — не отвечает наугад.</li></ul>
    <h3>Как гарантируется отсутствие выдумок</h3>
    <ol><li>Системная инструкция запрещает использовать знания модели: только результаты инструментов.</li>
      <li>Все вычисления — в SQL; база открыта в режиме <code>mode=ro</code>, разрешён только один <code>SELECT/WITH</code>.</li>
      <li>Модуль <code>verify.py</code> извлекает все числа из ответа (включая форматы «12,5 млрд», «1 234 567,89») и ищет их в результатах запросов. Неподтверждённые числа → модель переписывает ответ; если снова не подтверждено — ответ помечается предупреждением.</li>
      <li>Если в данных нет периода/товара/компании — агент отвечает «в данных ответа нет» и объясняет, чего не хватает.</li>
      <li>В интерфейсе видно, на чём основан ответ: SQL-запросы и строки результатов.</li></ol>
    <h3>Как проверялись ответы</h3>
    <ul><li>Автотесты (<code>pytest</code>): сопоставление колонок, разбор чисел, защита SQL, ловля выдуманного числа, цикл агента с фиктивной моделью.</li>
      <li>Контрольные вопросы с ответами, посчитанными вручную SQL-запросами, включая вопросы без ответа в данных (напр. «золото в 2023»).</li></ul>`
    : `
    <h3>Technology</h3>
    <ul><li><b>Backend:</b> Python 3, FastAPI, SQLite, pandas (file loading and normalisation).</li>
      <li><b>LLM:</b> Claude (Anthropic API) with tool use — the model never sees the raw data wholesale, it queries it with SQL.</li>
      <li><b>Frontend:</b> framework-free HTML/CSS/JS, SVG charts, RU/EN interface; the agent understands RU/UZ/EN questions.</li>
      <li><b>Account:</b> sign up / sign in (PBKDF2 password hashes, session tokens), watchlist, question history, file upload.</li></ul>
    <h3>Data preparation (uzex_spot_data registry)</h3>
    <ul><li>Every deal is linked to its contract card: currency, HS code, category. Party names come from the TIN, brokers from their code.</li>
      <li>Sellers spell the same product differently ("Мука", "МУКА ПШЕНИЧНАЯ…"), so a commodity = HS code with one name (42 commodities); the original name is kept. Fuel oil vs diesel and petrol in litres vs tonnes are split.</li>
      <li>Volume = lots × lot size, price = amount ÷ volume; diesel sold in kg is converted to tonnes.</li>
      <li>USD deals are converted to UZS at the rate on the deal date (<code>amount_uzs</code>).</li>
      <li>Cancelled (unpaid) deals are excluded from turnover, volume and prices; deal counts show them separately.</li></ul>
    <h3>Two agent modes</h3>
    <ul><li><b>Claude + SQL</b> — when an API key is set: any free-form question.</li>
      <li><b>Offline engine</b> — no key or API error: detects the commodity (RU/UZ/EN, word endings), period, conditions (export, spot/forward/futures, auction type) and metric (count, amount, top-N, average price and its trend, cancelled share, statuses, payment and delivery times, USD turnover) → ready SQL. If the question isn't understood, it doesn't guess.</li></ul>
    <h3>How we prevent made-up answers</h3>
    <ol><li>The system prompt forbids using model knowledge: tool results only.</li>
      <li>All calculations run in SQL; the DB is opened <code>mode=ro</code> and only a single <code>SELECT/WITH</code> is allowed.</li>
      <li><code>verify.py</code> extracts every number in the answer (incl. "12.5 bn", "1 234 567,89") and looks for it in the query results. Unconfirmed numbers → the model rewrites; if still unconfirmed → the answer carries a warning.</li>
      <li>If the period/commodity/company is not in the data, the agent says "the data has no answer" and explains what is missing.</li>
      <li>The UI shows what each answer is based on: SQL queries and result rows.</li></ol>
    <h3>How answers were checked</h3>
    <ul><li>Automated tests (<code>pytest</code>): column mapping, number parsing, SQL guard, catching an invented number, agent loop with a fake model.</li>
      <li>Control questions with answers computed by hand in SQL, including questions with no answer in the data (e.g. "gold in 2023").</li></ul>`}
    <h3>${ru ? "Загруженные данные" : "Loaded data"}</h3>
    <ul><li><code>deals</code> — ${fmt(d.total_rows)} (${dmy(d.date_range[0])} — ${dmy(d.date_range[1])})</li>${tables}</ul>
  </div>`;
}

// ---------------- mega menu ----------------
const L = (ru, en, href) => ({ ru, en, href });
const MENU = [
  { ru: "О нас", en: "About", cols: [
    { ru: "О бирже", en: "About the exchange", items: [L("Общая информация", "General information", "#/info/general"), L("Руководство", "Management", "#/info/management"), L("История", "History", "#/info/history"), L("Карта сайта", "Site map", "#/info/sitemap"), L("FAQ", "FAQ", "#/info/faq"), L("Контакты", "Contacts", "#/info/contacts")] },
    { ru: "О решении", en: "About the solution", items: [L("Описание решения", "Solution description", "#/about"), L("AI-агент", "AI agent", "#/agent"), L("Как проверяются ответы", "How answers are verified", "#/about")] },
  ] },
  { ru: "Рынки", en: "Markets", cols: [
    { ru: "Рынки", en: "Markets", items: [L("Торговые площадки", "Trading boards", "#/info/boards"), L("График торгов", "Trading schedule", "#/info/schedule"), L("Виды заявок", "Order types", "#/info/orders"), L("Тарифы", "Tariffs", "#/info/tariffs")] },
    { ru: "Нормативная база", en: "Regulations", items: [L("Правила", "Rules", "#/info/rules"), L("Положения", "Provisions", "#/info/provisions"), L("Порядки", "Procedures", "#/info/procedures")] },
    { ru: "Рыночные данные", en: "Market data", items: [L("Итоги торгов", "Trading results", "#/trades"), L("Список сделок по акциям", "Share trades list", "#/trades"), L("Ликвидность акций", "Share liquidity", "#/stocks?liq=high"), L("Курс доллара", "USD rate", "#/usd")] },
    { ru: "Товарная биржа", en: "Commodity exchange", items: [L("Котировки товаров", "Commodity quotes", "#/commodities"), L("Реестр сделок", "Deal registry", "#/deals"), L("Участники торгов", "Trading participants", "#/participants")] },
  ] },
  { ru: "Инструменты", en: "Instruments", cols: [
    { ru: "Инструменты", en: "Instruments", items: [L("Акции", "Stocks", "#/stocks"), L("Котировальный лист", "Quotation list", "#/listing"), L("Биржевые товары", "Commodities", "#/commodities")] },
    { ru: "Показатели", en: "Indicators", items: [L("Оборот по месяцам", "Monthly turnover", "#/"), L("Уровни ликвидности", "Liquidity levels", "#/stocks"), L("Курс USD/UZS", "USD/UZS rate", "#/usd")] },
  ] },
  { ru: "Участникам", en: "Participants", cols: [
    { ru: "Инвесторам", en: "Investors", items: [L("Как начать инвестировать", "How to start investing", "#/info/invest"), L("Члены биржи (Брокеры)", "Exchange members (brokers)", "#/participants"), L("Котировальный лист", "Quotation list", "#/listing"), L("Личный кабинет", "Personal account", "#/cabinet")] },
    { ru: "Эмитентам", en: "Issuers", items: [L("Листинг", "Listing", "#/info/listing"), L("Требования к эмитентам", "Issuer requirements", "#/info/issuers"), L("Раскрытие информации", "Disclosure", "#/info/disclosure")] },
    { ru: "Членам биржи", en: "Exchange members", items: [L("Документы для участников", "Documents for members", "#/info/docs"), L("Участники торгов", "Trading participants", "#/participants")] },
  ] },
  { ru: "Пресс-центр", en: "Press centre", cols: [
    { ru: "Медиацентр", en: "Media centre", items: [L("Новости", "News", "#/info/news"), L("Объявления", "Announcements", "#/info/announcements")] },
    { ru: "Аналитика", en: "Analytics", items: [L("Торговая статистика", "Trading statistics", "#/"), L("AI-аналитика по данным", "AI data analytics", "#/agent")] },
  ] },
  { ru: "Корпоративное управление", en: "Corporate governance", cols: [
    { ru: "Раскрытие информации", en: "Disclosure", items: [L("Существенные факты", "Material facts", "#/info/facts"), L("Дивиденды", "Dividends", "#/info/dividends")] },
    { ru: "Документы", en: "Documents", items: [L("Устав общества", "Charter", "#/info/charter"), L("Внутренние документы", "Internal documents", "#/info/internal")] },
  ] },
];
const tl = o => o[LANG] || o.ru;
function buildNav() {
  const cur = location.hash.split("?")[0] || "#/";
  const owner = ["#/", "#/agent", "#/about"].includes(cur) ? -1 : MENU.findIndex(m => m.cols.some(c => c.items.some(it => !it.href.includes("?") && it.href === cur)));
  $("#nav").innerHTML = MENU.map((m, i) => {
    const active = i === owner;
    return `<div class="mi" data-i="${i}"><button type="button" class="${active ? "on" : ""}" aria-expanded="false">${tl(m)}</button>
      <div class="mega" style="--cols:${m.cols.length}">${m.cols.map(c => `<div class="mega-col"><h4>${tl(c)}</h4>${c.items.map(it => `<a href="${it.href}">${tl(it)}</a>`).join("")}</div>`).join("")}</div></div>`;
  }).join("") + `<div class="mi"><a href="#/agent" class="nav-ai">${t("nav.agent")}</a></div>`;
}
const desktopNav = () => matchMedia("(min-width: 1181px)").matches;
function closeMenus(except) {
  document.querySelectorAll(".nav .mi.open").forEach(m => { if (m !== except) { m.classList.remove("open"); m.firstElementChild.setAttribute("aria-expanded", "false"); } });
}
$("#nav").addEventListener("click", e => {
  const b = e.target.closest(".mi > button");
  if (b) { const mi = b.parentElement; closeMenus(mi); const o = mi.classList.toggle("open"); b.setAttribute("aria-expanded", o); return; }
  if (e.target.closest("a")) { closeMenus(); $("#nav").classList.remove("open"); }
});
$("#nav").addEventListener("mouseover", e => {
  if (!desktopNav()) return;
  const mi = e.target.closest(".mi"); if (!mi || !mi.querySelector(".mega")) return;
  closeMenus(mi); mi.classList.add("open");
});
$("#nav").addEventListener("mouseleave", () => { if (desktopNav()) closeMenus(); });
document.addEventListener("click", e => { if (!e.target.closest(".nav")) closeMenus(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") { closeMenus(); closeSearch(); } });

// ---------------- search ----------------
let searchIdx = null;
async function buildSearchIndex() {
  const [st, tk, pt] = await Promise.all([cached("stocks", () => api("/api/stocks")), cached("ticker", () => api("/api/market/ticker")), api("/api/participants").catch(() => [])]);
  const pages = MENU.flatMap(m => m.cols.flatMap(c => c.items.map(it => ({ label: tl(it), href: it.href, kind: tl(m) }))));
  return [
    ...st.map(s => ({ label: `${s.ticker} — ${s.issuer}`, href: `#/stock/${s.ticker}`, kind: t("nav.stocks") })),
    ...tk.map(c => ({ label: `${c.name} (${c.code})`, href: `#/commodity/${encodeURIComponent(c.code)}`, kind: t("nav.commodities") })),
    ...pt.map(p => ({ label: p.name, href: `#/deals?q=${encodeURIComponent(p.name)}`, kind: t("part.list") })),
    ...pages,
  ];
}
function srchNorm(s) {
  const tr = { а: "a", б: "b", в: "v", г: "g", д: "d", е: "e", ё: "yo", ж: "j", з: "z", и: "i", й: "y", к: "k", л: "l", м: "m", н: "n", о: "o", п: "p", р: "r", с: "s", т: "t", у: "u", ф: "f", х: "x", ц: "ts", ч: "ch", ш: "sh", щ: "sh", ъ: "", ы: "i", ь: "", э: "e", ю: "yu", я: "ya" };
  const l = String(s).toLowerCase().replace(/[’ʻʼ`‘']/g, "");
  return l + " " + [...l].map(c => tr[c] ?? c).join("");
}
function openSearch() {
  $("#searchOv").hidden = false; $("#searchIn").placeholder = t("search.ph"); $("#searchIn").value = ""; $("#searchRes").innerHTML = "";
  $("#searchIn").focus(); buildSearchIndex().then(i => searchIdx = i).catch(() => {});
}
function closeSearch() { $("#searchOv").hidden = true; }
$("#searchBtn").onclick = openSearch;
$("#searchX").onclick = closeSearch;
$("#searchOv").onclick = e => { if (e.target.id === "searchOv") closeSearch(); };
$("#searchIn").oninput = async () => {
  const raw = $("#searchIn").value.trim(), q = srchNorm(raw).split(" ")[0];
  if (!searchIdx) searchIdx = await buildSearchIndex();
  if (!raw) { $("#searchRes").innerHTML = ""; return; }
  const qs = [raw.toLowerCase().replace(/[’ʻʼ`‘']/g, ""), srchNorm(raw).split(" ").slice(-1)[0]];
  const hits = searchIdx.filter(x => { const n = srchNorm(x.label); return qs.some(s => s && n.includes(s)); }).slice(0, 12);
  $("#searchRes").innerHTML = hits.map((h, i) => `<a href="${h.href}" class="${i ? "" : "sel"}">${esc(h.label)}<small>${esc(h.kind)}</small></a>`).join("")
    + `<a href="#/agent" data-q="${esc(raw)}" class="${hits.length ? "" : "sel"}">✦ ${t("search.ask")}: «${esc(raw)}»<small>${t("nav.agent")}</small></a>`;
};
$("#searchIn").onkeydown = e => { if (e.key === "Enter") { e.preventDefault(); $("#searchRes a.sel")?.click(); } };
$("#searchRes").addEventListener("click", e => { if (e.target.closest("a")) closeSearch(); });

// ---------------- extra pages ----------------
async function pageTrades(params) {
  const tk = (params.get("ticker") || "").toUpperCase();
  const [rows, st] = await Promise.all([api("/api/stocks/trades?limit=200" + (tk ? "&ticker=" + encodeURIComponent(tk) : "")), cached("stocks", () => api("/api/stocks"))]);
  return `<div class="page-h"><h1>${t("sec.trades")}</h1><p>${t("trades.text")}</p></div>${await demoNote()}
    <div class="card" style="margin-bottom:18px"><div class="filters"><label>${t("th.ticker")}<select id="trTk"><option value="">${t("all")}</option>${st.map(s => `<option ${s.ticker === tk ? "selected" : ""}>${esc(s.ticker)}</option>`).join("")}</select></label></div></div>
    ${tradesTable(rows)}`;
}
function afterTrades() { $("#trTk").onchange = e => location.hash = "#/trades" + (e.target.value ? "?ticker=" + e.target.value : ""); }

async function pageListing() {
  const [lst, st] = await Promise.all([cached("lst", () => api("/api/stocks/listings")), cached("stocks", () => api("/api/stocks"))]);
  const liq = Object.fromEntries(st.map(s => [s.ticker, s.months]));
  return `<div class="page-h"><h1>${t("sec.listings")}</h1></div>${await demoNote()}
  <div class="card tbl-wrap"><table><thead><tr><th>${t("th.logo")}</th><th>${t("th.ticker")}</th><th>${t("th.issuer")}</th><th>${t("th.listed")}</th><th>${t("th.currency")}</th><th class="r">${t("th.nominal")}</th><th class="r">${t("th.count")}</th><th class="r">${t("th.liq")}</th></tr></thead><tbody>
    ${lst.map(r => `<tr class="clk" data-href="#/stock/${esc(r.ticker)}"><td><div class="logo-chip">${ini(r.issuer || r.ticker)}</div></td><td><b>${esc(r.ticker)}</b></td><td>${esc(r.issuer)}</td><td class="num">${dmy(r.listed_date)}</td><td>${esc(r.currency)}</td><td class="r num">${fmt(r.nominal)}</td><td class="r num">${fmt(r.shares)}</td><td class="r">${liqBadge(liq[r.ticker] ?? 0)}</td></tr>`).join("")}
  </tbody></table></div>`;
}

async function pageUsd() {
  const rows = await api("/api/usd");
  if (!rows.length) return `<div class="empty">${t("notfound")}</div>`;
  const last = rows[rows.length - 1], prev = rows[rows.length - 2] || last, ch = last.usd_uzs - prev.usd_uzs;
  return `<div class="page-h"><h1>${t("usd.title")}</h1><p>${t("usd.text")}</p></div>${await demoNote()}
  <div class="card pad" style="margin-bottom:18px"><div class="dt-head"><div class="logo-chip">$</div><div><h1>USD / UZS</h1><div class="muted">${dmy(last.date)}</div></div>
    <div class="dt-price"><b class="num">${fmt(last.usd_uzs, 2)}</b><span class="num ${cls(ch)}">${sign(ch)}${fmt(ch, 2)}</span></div></div></div>
  <div class="grid g2">
    <div class="card pad">${lineChart(rows.filter((_, i) => i % 5 === 0 || i === rows.length - 1).map(r => ({ x: dmy(r.date), y: r.usd_uzs })), { fmtY: v => fmt(v, 0) })}</div>
    <div class="card tbl-wrap" style="max-height:340px;overflow:auto"><table><thead><tr><th>${t("th.date")}</th><th class="r">USD/UZS</th></tr></thead><tbody>
      ${rows.slice(-60).reverse().map(r => `<tr><td class="num">${dmy(r.date)}</td><td class="r num">${fmt(r.usd_uzs, 2)}</td></tr>`).join("")}</tbody></table></div>
  </div>`;
}

async function pageInfo(slug) {
  const item = MENU.flatMap(m => m.cols.flatMap(c => c.items.map(it => ({ it, c, m })))).find(x => x.it.href === "#/info/" + slug);
  if (!item) throw Object.assign(new Error(t("notfound")), { status: 404 });
  const links = item.c.items.filter(x => x !== item.it);
  return `<a class="muted" href="#/">${t("back")}</a>
  <div class="page-h" style="margin-top:12px"><small class="muted" style="text-transform:uppercase;letter-spacing:.1em;font-weight:700">${tl(item.m)} · ${tl(item.c)}</small><h1>${tl(item.it)}</h1></div>
  <div class="card pad prose"><p>${t("info.text")}</p>
    <div class="info-links"><a class="btn sm" href="#/agent">${t("nav.agent")}</a><a class="btn ghost sm" href="#/deals">${t("nav.deals")}</a><a class="btn ghost sm" href="#/stocks">${t("nav.stocks")}</a></div>
    ${links.length ? `<h3>${tl(item.c)}</h3><ul>${links.map(l => `<li><a href="${l.href}">${tl(l)}</a></li>`).join("")}</ul>` : ""}
  </div>`;
}

// ---------------- router ----------------
const USD_TODAY = { rate: 12020, date: "2026-11-05" }; // текущий курс для главной; агент считает по usd_rates.csv
const ROUTES = [
  [/^\/$/, pageHome, afterHome, "/"],
  [/^\/stocks$/, pageStocks, afterStocks, "/stocks"],
  [/^\/stock\/([^/]+)$/, pageStock, null, "/stocks"],
  [/^\/commodities$/, pageCommodities, null, "/commodities"],
  [/^\/commodity\/([^/]+)$/, pageCommodity, null, "/commodities"],
  [/^\/deals$/, pageDeals, afterDeals, "/deals"],
  [/^\/participants$/, pageParticipants, afterParticipants, "/participants"],
  [/^\/agent$/, pageAgent, afterAgent, "/agent"],
  [/^\/cabinet$/, pageCabinet, afterCabinet, null],
  [/^\/about$/, pageAbout, null, "/about"],
  [/^\/trades$/, pageTrades, afterTrades, "/trades"],
  [/^\/listing$/, pageListing, null, "/listing"],
  [/^\/usd$/, pageUsd, null, "/usd"],
  [/^\/info\/([\w-]+)$/, pageInfo, null, null],
];
let routeSeq = 0;
async function route() {
  const seq = ++routeSeq;
  const [path, qs] = (location.hash.slice(1) || "/").split("?");
  const params = new URLSearchParams(qs || "");
  const app = $("#app");
  $("#nav").classList.remove("open");
  closeMenus();
  for (const [re, page, after, navKey] of ROUTES) {
    const m = path.match(re);
    if (!m) continue;
    buildNav();
    app.innerHTML = `<div class="skel">${t("loading")}</div>`;
    try {
      const html = await (m[1] ? page(decodeURIComponent(m[1]), params) : page(params));
      if (seq !== routeSeq) return;
      app.innerHTML = html;
      after?.(params);
    } catch (e) {
      if (seq !== routeSeq) return;
      app.innerHTML = `<div class="empty">${e.status === 404 ? t("notfound") : esc(e.message)}</div>`;
    }
    if (!history.state?.keep) scrollTo(0, 0);
    return;
  }
  app.innerHTML = `<div class="empty">${t("notfound")}</div>`;
}
addEventListener("hashchange", route);

(async () => {
  await loadMe();
  applyI18n();
  renderTape();
  footer();
  route();
  setInterval(() => { delete cache.ticker; renderTape(); }, 60000);
})();
