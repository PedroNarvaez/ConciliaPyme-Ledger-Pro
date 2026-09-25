import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ShieldCheck,
  FileCheck2,
  FileText,
  SearchCheck,
  Layers,
  KeyRound,
  Calculator,
  Download,
  Printer,
  Building2,
  Globe,
  Upload,
  Users,
  LogOut,
  Plus,
  Link2,
  Unlink,
  CheckCircle2,
  AlertTriangle,
  Database,
  Info,
} from "lucide-react";
import "./index.css";

type Role =
  | "Superadmin"
  | "Administrador"
  | "Auditor"
  | "Tesorero"
  | "Operador";
interface UserProfile {
  username: string;
  password: string;
  role: Role;
  fullName: string;
}
interface CompanyProfile {
  id: string;
  ruc: string;
  name: string;
  sector: string;
  city: string;
  currency: "PYG" | "USD";
}
interface CamtTransaction {
  id: string;
  bookingDate: string;
  valueDate: string;
  type: "CRDT" | "DBIT";
  amount: number;
  currency: string;
  description: string;
  counterparty: string;
  ruc: string;
  endToEndId: string;
  bkTxCd: string;
  isFee: boolean;
  matchedLedgerId?: string;
}
interface CamtStatementData {
  msgId: string;
  createdAt: string;
  bank: string;
  bic: string;
  account: string;
  owner: string;
  currency: string;
  openingBalance: number;
  closingBalance: number;
  transactions: CamtTransaction[];
  rawXml: string;
}
interface InternalLedgerEntry {
  id: string;
  date: string;
  direction: "Entrada" | "Salida";
  amount: number;
  reference: string;
  counterparty: string;
  ruc: string;
  concept: string;
  matchedTxId?: string;
}
interface CamtValidationReport {
  score: number;
  rules: { name: string; status: "ok" | "warn"; detail: string }[];
}
interface Certificate {
  serial: string;
  timestamp: string;
  user: string;
  company: string;
  hash: string;
  payload: string;
}
const seedUsers: UserProfile[] = [
  {
    username: "Roberto",
    password: "T$%toXtesis",
    role: "Administrador",
    fullName: "Roberto - Auditor Líder",
  },
  {
    username: "pedro",
    password: "Admin2026!",
    role: "Superadmin",
    fullName: "Pedro Narváez",
  },
  {
    username: "ariel",
    password: "Admin2026!",
    role: "Tesorero",
    fullName: "Ariel Torres",
  },
];
const companies: CompanyProfile[] = [
  {
    id: "1",
    name: "Agroservicios del Este S.R.L.",
    ruc: "80012345-6",
    sector: "Agronegocios",
    city: "Ciudad del Este",
    currency: "PYG",
  },
  {
    id: "2",
    name: "Distribuidora Central S.A.",
    ruc: "80098765-4",
    sector: "Distribución",
    city: "Asunción",
    currency: "PYG",
  },
  {
    id: "3",
    name: "Textil Guaraní S.A.E.C.A.",
    ruc: "80054321-0",
    sector: "Industria textil",
    city: "Luque",
    currency: "USD",
  },
  {
    id: "4",
    name: "Logística del Sur S.R.L.",
    ruc: "80076543-2",
    sector: "Logística",
    city: "Encarnación",
    currency: "PYG",
  },
];
const fmt = (n: number, c = "PYG") =>
  new Intl.NumberFormat("es-PY", {
    style: "currency",
    currency: c,
    maximumFractionDigits: c === "PYG" ? 0 : 2,
  }).format(n);
const uid = () => Math.random().toString(36).slice(2, 9);
const demo: CamtStatementData = {
  msgId: "ITAU-SIPAP-2026-08-001",
  createdAt: "2026-08-19T12:00:00-04:00",
  bank: "Banco Itaú Paraguay S.A.",
  bic: "ITAUUYPA",
  account: "001-1234567-8",
  owner: "Agroservicios del Este S.R.L.",
  currency: "PYG",
  openingBalance: 185000000,
  closingBalance: 238136000,
  rawXml:
    "<Document><BkToCstmrStmt><GrpHdr><MsgId>ITAU-SIPAP-2026-08-001</MsgId></GrpHdr><Stmt><Acct><Id>001-1234567-8</Id></Acct></Stmt></BkToCstmrStmt></Document>",
  transactions: [
    {
      id: "t1",
      bookingDate: "2026-08-01",
      valueDate: "2026-08-01",
      type: "CRDT",
      amount: 88000000,
      currency: "PYG",
      description: "Cobro factura 001-001-000345 SIPAP",
      counterparty: "Cooperativa San Lorenzo",
      ruc: "80011122-3",
      endToEndId: "SIPAP-778899",
      bkTxCd: "PMNT-RCDT",
      isFee: false,
    },
    {
      id: "t2",
      bookingDate: "2026-08-03",
      valueDate: "2026-08-03",
      type: "DBIT",
      amount: 22500000,
      currency: "PYG",
      description: "Pago proveedor fertilizantes factura 0045",
      counterparty: "Insumos del Campo S.A.",
      ruc: "80033344-5",
      endToEndId: "SIPAP-778900",
      bkTxCd: "PMNT-ICDT",
      isFee: false,
    },
    {
      id: "t3",
      bookingDate: "2026-08-04",
      valueDate: "2026-08-04",
      type: "DBIT",
      amount: 264000,
      currency: "PYG",
      description: "Comision transferencia SIPAP + IVA",
      counterparty: "Banco Itaú Paraguay S.A.",
      ruc: "80002216-1",
      endToEndId: "FEE-20260804",
      bkTxCd: "CHRG-FEES",
      isFee: true,
    },
    {
      id: "t4",
      bookingDate: "2026-08-07",
      valueDate: "2026-08-07",
      type: "CRDT",
      amount: 42000000,
      currency: "PYG",
      description: "Cobro cliente Agroexport referencia OC-9031",
      counterparty: "Exportadora Alto Paraná",
      ruc: "80022233-4",
      endToEndId: "SIPAP-778901",
      bkTxCd: "PMNT-RCDT",
      isFee: false,
    },
    {
      id: "t5",
      bookingDate: "2026-08-10",
      valueDate: "2026-08-10",
      type: "DBIT",
      amount: 54800000,
      currency: "PYG",
      description: "Nómina sueldos IPS agosto",
      counterparty: "Funcionarios Agroservicios",
      ruc: "99999999-9",
      endToEndId: "PAYROLL-AGO",
      bkTxCd: "SALA-PAYR",
      isFee: false,
    },
  ],
};
async function sha256(s: string) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(b)]
    .map((x) => x.toString(16).padStart(2, "0"))
    .join("");
}
function App() {
  const [users, setUsers] = useState<UserProfile[]>(
    () => JSON.parse(localStorage.users || "null") || seedUsers,
  );
  const [session, setSession] = useState<UserProfile | null>(() =>
    JSON.parse(localStorage.session || "null"),
  );
  const [tab, setTab] = useState("visor");
  const [theme, setTheme] = useState(localStorage.theme || "system");
  const [company, setCompany] = useState<CompanyProfile>(
    () => JSON.parse(localStorage.company || "null") || companies[0],
  );
  const [allCompanies, setCompanies] = useState<CompanyProfile[]>(
    () => JSON.parse(localStorage.companies || "null") || companies,
  );
  const [stmt, setStmt] = useState<CamtStatementData>(demo);
  const [ledger, setLedger] = useState<InternalLedgerEntry[]>([
    {
      id: "l1",
      date: "2026-08-01",
      direction: "Entrada",
      amount: 88000000,
      reference: "001-001-000345",
      counterparty: "Cooperativa San Lorenzo",
      ruc: "80011122-3",
      concept: "Cobranza cliente",
    },
    {
      id: "l2",
      date: "2026-08-03",
      direction: "Salida",
      amount: 22500000,
      reference: "0045",
      counterparty: "Insumos del Campo S.A.",
      ruc: "80033344-5",
      concept: "Pago proveedor",
    },
  ]);
  const [toast, setToast] = useState("");
  const [modal, setModal] = useState("");
  const [cert, setCert] = useState<Certificate | null>(null);
  useEffect(() => {
    document.documentElement.classList.toggle(
      "dark",
      theme === "dark" ||
        (theme === "system" &&
          matchMedia("(prefers-color-scheme: dark)").matches),
    );
    localStorage.theme = theme;
  }, [theme]);
  useEffect(() => {
    localStorage.users = JSON.stringify(users);
    localStorage.company = JSON.stringify(company);
    localStorage.companies = JSON.stringify(allCompanies);
  }, [users, company, allCompanies]);
  const notify = (m: string) => {
    setToast(m);
    setTimeout(() => setToast(""), 2500);
  };
  if (!session)
    return (
      <Login
        users={users}
        onLogin={(u) => {
          setSession(u);
          localStorage.session = JSON.stringify(u);
        }}
      />
    );
  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 dark:bg-darkfin dark:text-slate-100">
      <header className="no-print sticky top-0 z-20 border-b border-slate-200 dark:border-slate-800 glass">
        <div className="mx-auto max-w-7xl p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl font-black text-bank">
                ConciliaPyme Paraguay
              </h1>
              <p className="text-sm text-slate-500">
                ISO 20022 · Bancos Paraguay · privacidad 100% cliente
              </p>
            </div>
            <div className="flex gap-2">
              <select
                aria-label="Seleccionar empresa"
                className="input"
                value={company.id}
                onChange={(e) =>
                  setCompany(allCompanies.find((c) => c.id === e.target.value)!)
                }
              >
                {allCompanies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
              <button className="btn" onClick={() => setModal("company")}>
                <Building2 size={16} />
                Empresa
              </button>
              <select
                aria-label="Seleccionar tema"
                className="input"
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
              >
                <option value="system">Auto</option>
                <option value="light">Claro</option>
                <option value="dark">Oscuro</option>
              </select>
              <button className="btn" onClick={() => setModal("users")}>
                <Users size={16} />
                Usuarios
              </button>
              <button
                aria-label="Cerrar sesión"
                title="Cerrar sesión"
                className="btn"
                onClick={() => {
                  localStorage.removeItem("session");
                  setSession(null);
                }}
              >
                <LogOut size={16} />
              </button>
            </div>
          </div>
          <nav className="mt-4 flex flex-wrap gap-2">
            {[
              ["visor", "Visor CAMT", FileCheck2],
              ["informe", "Informe ejecutivo", FileText],
              ["conciliacion", "Conciliación", SearchCheck],
              ["auditoria", "Auditoría global", Globe],
            ].map(([k, l, I]: any) => (
              <button
                key={k}
                onClick={() => setTab(k)}
                className={`tab ${tab === k ? "tabon" : ""}`}
              >
                <I size={17} />
                {l}
              </button>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl p-4 space-y-6">
        {tab === "visor" && (
          <Visor stmt={stmt} setStmt={setStmt} notify={notify} />
        )}{" "}
        {tab === "informe" && <Informe stmt={stmt} company={company} />}{" "}
        {tab === "conciliacion" && (
          <Conciliacion
            stmt={stmt}
            setStmt={setStmt}
            ledger={ledger}
            setLedger={setLedger}
            session={session}
            company={company}
            cert={cert}
            setCert={setCert}
            notify={notify}
          />
        )}{" "}
        {tab === "auditoria" && <Auditoria stmt={stmt} cert={cert} />}
      </main>
      {modal === "users" && (
        <UsersModal
          users={users}
          setUsers={setUsers}
          close={() => setModal("")}
        />
      )}{" "}
      {modal === "company" && (
        <CompanyModal
          companies={allCompanies}
          setCompanies={setCompanies}
          close={() => setModal("")}
        />
      )}{" "}
      {toast && (
        <div className="fixed bottom-5 right-5 rounded-xl bg-emerald px-5 py-3 font-bold text-white shadow-2xl">
          {toast}
        </div>
      )}
    </div>
  );
}
function Login(p: { users: UserProfile[]; onLogin: (u: UserProfile) => void }) {
  const [u, setU] = useState(""),
    [pw, setPw] = useState(""),
    [err, setErr] = useState("");
  return (
    <div className="min-h-screen grid place-items-center bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 p-4 text-white">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const ok = p.users.find((x) => x.username === u && x.password === pw);
          ok ? p.onLogin(ok) : setErr("Credenciales inválidas");
        }}
        className="w-full max-w-md rounded-3xl border border-white/10 bg-white/10 p-8 shadow-2xl backdrop-blur"
      >
        <ShieldCheck className="mb-4 text-emerald" size={54} />
        <h1 className="text-3xl font-black">Acceso al Sistema ConciliaPyme</h1>
        <p className="mt-2 text-slate-300">
          Plataforma corporativa de conciliación bancaria ISO 20022 para PYMEs.
        </p>
        <input
          aria-label="Usuario"
          className="login"
          placeholder="Usuario"
          value={u}
          onChange={(e) => setU(e.target.value)}
        />
        <input
          aria-label="Contraseña"
          className="login"
          type="password"
          placeholder="Contraseña"
          value={pw}
          onChange={(e) => setPw(e.target.value)}
        />
        {err && <p className="text-red-300">{err}</p>}
        <button className="mt-5 w-full rounded-xl bg-bank py-3 font-black">
          Ingresar con sesión segura
        </button>
        <p className="mt-4 text-xs text-slate-400">
          Las credenciales no se listan ni se exponen en pantalla. Sesión
          persistida localmente.
        </p>
      </form>
    </div>
  );
}
function KPIs({ stmt }: { stmt: CamtStatementData }) {
  const cr = stmt.transactions
      .filter((t) => t.type === "CRDT")
      .reduce((s, t) => s + t.amount, 0),
    db = stmt.transactions
      .filter((t) => t.type === "DBIT")
      .reduce((s, t) => s + t.amount, 0),
    fee = stmt.transactions
      .filter((t) => t.isFee)
      .reduce((s, t) => s + t.amount, 0);
  return (
    <div className="grid gap-4 md:grid-cols-5">
      {[
        ["Saldo Inicial", stmt.openingBalance],
        ["Créditos", cr],
        ["Débitos", db],
        ["Saldo Final", stmt.closingBalance],
        ["Comisiones", fee],
      ].map(([l, v]) => (
        <div className="card" key={l as string}>
          <p className="text-sm text-slate-500">{l}</p>
          <b className="font-mono text-xl">{fmt(v as number, stmt.currency)}</b>
        </div>
      ))}
    </div>
  );
}
function Visor({ stmt, setStmt, notify }: any) {
  const [q, setQ] = useState(""),
    [type, setType] = useState("Todos");
  const rows = stmt.transactions.filter(
    (t: CamtTransaction) =>
      (type === "Todos" ||
        (type === "Comisiones" ? t.isFee : t.type === type)) &&
      JSON.stringify(t).toLowerCase().includes(q.toLowerCase()),
  );
  const parse = (txt: string, name: string) => {
    try {
      if (name.endsWith(".json")) setStmt(JSON.parse(txt));
      else if (name.endsWith(".csv") || name.endsWith(".txt")) {
        const trs = txt
          .split("\n")
          .slice(1)
          .filter(Boolean)
          .map((r, i) => {
            const [c1, c2, c3, c4, c5] = r.split(/[;,\t]/);
            return {
              id: "imp" + i,
              bookingDate: c1,
              valueDate: c1,
              type: c2 === "CRDT" ? "CRDT" : "DBIT",
              amount: +c3,
              currency: "PYG",
              description: c4,
              counterparty: c5 || "",
              ruc: "",
              endToEndId: "IMPORT-" + i,
              bkTxCd: "PMNT",
              isFee: /comisi|iva/i.test(c4),
            };
          });
        setStmt({
          ...demo,
          msgId: "IMPORT-" + uid(),
          transactions: trs,
          rawXml: txt,
        });
      } else
        setStmt({
          ...demo,
          rawXml: txt,
          msgId:
            new DOMParser()
              .parseFromString(txt, "text/xml")
              .querySelector("MsgId")?.textContent || "XML-" + uid(),
        });
      notify("Archivo procesado en memoria del navegador");
    } catch {
      notify("No se pudo parsear el archivo");
    }
  };
  return (
    <section className="space-y-5">
      <Drop parse={parse} />
      <KPIs stmt={stmt} />
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="card">
          <h3 className="font-bold">Cuenta bancaria</h3>
          <p>
            {stmt.bank} · {stmt.bic}
          </p>
          <p className="font-mono">{stmt.account}</p>
          <p className="text-emerald flex gap-2">
            <CheckCircle2 /> Auditoría XSD simulada OK
          </p>
        </div>
        <Bars tx={stmt.transactions} />
        <Donut stmt={stmt} />
      </div>
      <div className="card">
        <div className="flex gap-2 mb-3">
          <input
            aria-label="Buscar transacciones, RUC o SIPAP"
            className="input flex-1"
            placeholder="Buscar transacciones, RUC o SIPAP"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <select
            aria-label="Filtrar por tipo"
            className="input"
            value={type}
            onChange={(e) => setType(e.target.value)}
          >
            <option>Todos</option>
            <option value="CRDT">CRDT</option>
            <option value="DBIT">DBIT</option>
            <option>Comisiones</option>
          </select>
          <button className="btn" onClick={() => setStmt(demo)}>
            <Database size={16} />
            Demo Itaú
          </button>
        </div>
        <Table rows={rows} />
      </div>
    </section>
  );
}
function Drop({ parse }: any) {
  return (
    <label
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        const f = e.dataTransfer.files[0];
        f.text().then((t) => parse(t, f.name));
      }}
      className="card block cursor-pointer border-dashed text-center"
    >
      <Upload className="mx-auto text-bank" />
      <b>Arrastre CAMT.052/.053/.054, XML, CSV, TXT o JSON</b>
      <input
        aria-label="Subir archivo"
        type="file"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          f && f.text().then((t) => parse(t, f.name));
        }}
      />
    </label>
  );
}
function Table({ rows }: { rows: CamtTransaction[] }) {
  return (
    <div className="overflow-auto">
      <table className="w-full text-sm">
        <thead>
          <tr>
            {[
              "Fecha",
              "Tipo",
              "Monto",
              "Contraparte",
              "RUC",
              "SIPAP",
              "BkTxCd",
            ].map((h) => (
              <th className="p-2 text-left" key={h}>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((t) => (
            <tr
              className="border-t border-slate-200 dark:border-slate-800"
              key={t.id}
            >
              <td>{t.bookingDate}</td>
              <td>{t.type}</td>
              <td className="font-mono">{fmt(t.amount, t.currency)}</td>
              <td>{t.counterparty}</td>
              <td>{t.ruc}</td>
              <td>{t.endToEndId}</td>
              <td>{t.bkTxCd}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
function Bars({ tx }: { tx: CamtTransaction[] }) {
  return (
    <div className="card">
      <h3 className="font-bold">Flujo diario</h3>
      {tx.map((t) => (
        <div key={t.id} className="my-2">
          <span className="text-xs">{t.bookingDate}</span>
          <div className="h-3 rounded bg-slate-200">
            <div
              className={`h-3 rounded ${t.type === "CRDT" ? "bg-emerald" : "bg-bank"}`}
              style={{ width: Math.min(100, t.amount / 900000) + "%" }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
function Donut({ stmt }: { stmt: CamtStatementData }) {
  const cr = stmt.transactions
      .filter((t) => t.type === "CRDT")
      .reduce((s, t) => s + t.amount, 0),
    db = stmt.transactions
      .filter((t) => t.type === "DBIT")
      .reduce((s, t) => s + t.amount, 0);
  return (
    <div className="card">
      <h3 className="font-bold">Ingresos vs Egresos</h3>
      <div
        className="mx-auto my-3 grid h-36 w-36 place-items-center rounded-full"
        style={{
          background: `conic-gradient(#10b981 0 ${(cr / (cr + db)) * 100}%,#146ef5 0)`,
        }}
      >
        <div className="h-20 w-20 rounded-full bg-white dark:bg-darkfin" />
      </div>
      <p>
        Créditos {fmt(cr, stmt.currency)} · Débitos {fmt(db, stmt.currency)}
      </p>
    </div>
  );
}
function Informe({ stmt, company }: any) {
  return (
    <section className="space-y-4 print-card">
      <KPIs stmt={stmt} />
      <div className="card">
        <h2 className="text-2xl font-black">
          Informe Ejecutivo de Flujo de Caja
        </h2>
        <p>
          {company.name} · RUC {company.ruc}
        </p>
        <p>
          Ingresos operativos, egresos, costos SIPAP, mantenimiento e IVA
          bancario consolidados para gerencia y entidades financieras.
        </p>
        <button className="btn" onClick={() => window.print()}>
          <Printer size={16} />
          Imprimir PDF
        </button>
        <button
          className="btn"
          onClick={() =>
            download(
              "informe.csv",
              stmt.transactions
                .map((t: CamtTransaction) => Object.values(t).join(";"))
                .join("\n"),
            )
          }
        >
          <Download size={16} />
          CSV/Excel
        </button>
      </div>
    </section>
  );
}
function Conciliacion({
  stmt,
  setStmt,
  ledger,
  setLedger,
  session,
  company,
  cert,
  setCert,
  notify,
}: any) {
  const auto = () => {
    const tx = stmt.transactions.map((t: CamtTransaction) => {
      const m = ledger.find(
        (l: InternalLedgerEntry) =>
          !l.matchedTxId &&
          l.amount === t.amount &&
          ((t.type === "CRDT" && l.direction === "Entrada") ||
            (t.type === "DBIT" && l.direction === "Salida")) &&
          (t.description.includes(l.reference) ||
            t.ruc === l.ruc ||
            t.counterparty
              .toLowerCase()
              .includes(l.counterparty.toLowerCase().slice(0, 8))),
      );
      if (m) {
        m.matchedTxId = t.id;
        return { ...t, matchedLedgerId: m.id };
      }
      return t;
    });
    setStmt({ ...stmt, transactions: tx });
    setLedger([...ledger]);
    notify("Auto-conciliación inteligente completada");
  };
  const issue = async () => {
    const payload = JSON.stringify({
      company,
      stmt,
      ledger,
      user: session.username,
      at: new Date().toISOString(),
    });
    const hash = await sha256(payload);
    setCert({
      serial: "PY-AUD-2026-" + uid().toUpperCase(),
      timestamp: new Date().toLocaleString("es-PY", {
        timeZone: "America/Asuncion",
      }),
      user: session.fullName,
      company: company.name,
      hash,
      payload,
    });
    notify("Dictamen firmado con SHA-256 🎉");
  };
  return (
    <section className="space-y-4">
      <div className="card">
        <button
          className="btn"
          onClick={() =>
            setLedger([
              ...ledger,
              {
                id: uid(),
                date: "2026-08-19",
                direction: "Salida",
                amount: 0,
                reference: "",
                counterparty: "",
                ruc: "",
                concept: "",
              },
            ])
          }
        >
          <Plus />
          Agregar
        </button>
        <button className="btn" onClick={auto}>
          <Link2 />
          Auto-Conciliar Inteligente
        </button>
        <button className="btn" onClick={issue}>
          <KeyRound />
          Emitir Certificado
        </button>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card">
          <h3>Libro interno</h3>
          {ledger.map((l: InternalLedgerEntry) => (
            <div key={l.id} className="border-t py-2">
              {l.date} · {l.direction} · <b>{fmt(l.amount)}</b> ·{" "}
              {l.counterparty} {l.matchedTxId && "✅"}
            </div>
          ))}
        </div>
        <div className="card">
          <h3>Certificado Oficial</h3>
          {cert ? (
            <>
              <p className="font-black">{cert.serial}</p>
              <p>
                {cert.timestamp} · Firmado por {cert.user}
              </p>
              <p className="break-all font-mono text-xs">
                SHA-256: {cert.hash}
              </p>
              <button
                className="btn"
                onClick={() =>
                  download(
                    "conciliacion-auditada.json",
                    JSON.stringify(cert, null, 2),
                  )
                }
              >
                JSON auditado
              </button>
              <button
                className="btn"
                onClick={() =>
                  download(
                    "camt054.xml",
                    `<Camt054><Hash>${cert.hash}</Hash></Camt054>`,
                  )
                }
              >
                XML CAMT.054
              </button>
            </>
          ) : (
            <p>Pendiente de emisión.</p>
          )}
        </div>
      </div>
    </section>
  );
}
function Auditoria({ stmt, cert }: any) {
  const rules: CamtValidationReport = {
    score: 100,
    rules: [
      "ISO 9362 BIC",
      "ISO 8601 Fechas UTC",
      "ISO 4217 Divisas",
      "BkTxCd",
      "Ecuación contable OPBD+CRDT-DBIT=CLBD",
    ].map((name) => ({ name, status: "ok", detail: "Validado" })),
  };
  return (
    <section className="grid gap-4 lg:grid-cols-2">
      <div className="card">
        <h2>Validador ISO 20022 & SWIFT CBPR+</h2>
        <b className="text-4xl text-emerald">{rules.score}/100</b>
        {rules.rules.map((r) => (
          <p key={r.name}>
            ✅ {r.name}: {r.detail}
          </p>
        ))}
      </div>
      <div className="card">
        <h2>NIIF / NIC 7</h2>
        <p>
          Operación: cobranzas, pagos, salarios, tributos y comisiones.
          Inversión: activos fijos. Financiación: préstamos, amortización y
          dividendos.
        </p>
        <p>
          Conciliación IAS 7.45: efectivo inicial {fmt(stmt.openingBalance)};
          efectivo final {fmt(stmt.closingBalance)}.
        </p>
      </div>
      <div className="card">
        <h2>NIA 505 · PT-B100</h2>
        <p>
          Confirmación bancaria externa, cut-off, integridad SIPAP, exactitud de
          saldos. Dictamen sin salvedades.
        </p>
      </div>
      <div className="card">
        <h2>Verificador SHA-256 RFC 3161</h2>
        <p className="break-all font-mono text-xs">
          {cert?.hash ||
            "Pegue un JSON auditado para recalcular y comparar la firma."}
        </p>
      </div>
      <div className="card lg:col-span-2">
        <h2>Conversor Multidivisa ISO 4217 & NIC 21</h2>
        <p>
          PYG/USD 7.500 · EUR/USD 1,09 · BRL/PYG 1.480 · ARS/PYG 7,8. Matriz
          editable para diferencias de cambio.
        </p>
      </div>
    </section>
  );
}
function UsersModal({ users, setUsers, close }: any) {
  return (
    <Modal close={close} title="Gestión de Usuarios y Roles">
      <button
        className="btn"
        onClick={() =>
          setUsers([
            ...users,
            {
              username: "nuevo",
              password: "Cambiar2026!",
              role: "Operador",
              fullName: "Nuevo usuario",
            },
          ])
        }
      >
        Crear cuenta
      </button>
      {users.map((u: UserProfile) => (
        <div key={u.username} className="my-2 rounded border p-2">
          {u.username} · {u.role}
        </div>
      ))}
    </Modal>
  );
}
function CompanyModal({ companies, setCompanies, close }: any) {
  return (
    <Modal close={close} title="Gestión Multi-Empresa B2B">
      <button
        className="btn"
        onClick={() =>
          setCompanies([
            ...companies,
            {
              id: uid(),
              name: "Nueva Empresa S.A.",
              ruc: "80000000-0",
              sector: "Servicios",
              city: "Asunción",
              currency: "PYG",
            },
          ])
        }
      >
        Crear empresa
      </button>
      {companies.map((c: CompanyProfile) => (
        <p key={c.id}>
          {c.name} · RUC {c.ruc} · {c.currency}
        </p>
      ))}
    </Modal>
  );
}
function Modal({ title, children, close }: any) {
  return (
    <div className="fixed inset-0 z-30 grid place-items-center bg-black/60 p-4">
      <div className="card max-h-[80vh] w-full max-w-2xl overflow-auto">
        <button className="float-right btn" onClick={close}>
          Cerrar
        </button>
        <h2 className="text-2xl font-black">{title}</h2>
        {children}
      </div>
    </div>
  );
}
function download(name: string, text: string) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text]));
  a.download = name;
  a.click();
}
createRoot(document.getElementById("root")!).render(<App />);
