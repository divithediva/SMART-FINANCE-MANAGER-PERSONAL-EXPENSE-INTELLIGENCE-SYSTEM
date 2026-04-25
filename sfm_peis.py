"""
Smart Finance Manager & Personal Expense Intelligence System (SFM-PEIS)
A comprehensive Python-based personal finance management application.
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as mticker


# ──────────────────────────────────────────────
# DATA MODELS
# ──────────────────────────────────────────────

CATEGORIES = [
    "Food & Dining", "Transportation", "Housing", "Healthcare",
    "Entertainment", "Shopping", "Utilities", "Education",
    "Travel", "Savings", "Income", "Subscriptions", "Other"
]

SUBSCRIPTION_KEYWORDS = ["netflix", "spotify", "amazon prime", "hulu", "youtube",
                          "gym", "magazine", "insurance", "adobe", "microsoft"]


class Transaction:
    def __init__(self, amount, category, description, date=None,
                 trans_type="expense", tag=None):
        self.id = str(uuid.uuid4())[:8]
        self.amount = float(amount)
        self.category = category
        self.description = description
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.type = trans_type          # "income" or "expense"
        self.tag = tag or ""

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
            "type": self.type,
            "tag": self.tag,
        }

    @staticmethod
    def from_dict(d):
        t = Transaction.__new__(Transaction)
        t.__dict__.update(d)
        return t


class Budget:
    def __init__(self, category, monthly_limit):
        self.category = category
        self.monthly_limit = float(monthly_limit)

    def to_dict(self):
        return {"category": self.category, "monthly_limit": self.monthly_limit}


class SavingsGoal:
    def __init__(self, name, target_amount, deadline):
        self.name = name
        self.target_amount = float(target_amount)
        self.current_amount = 0.0
        self.deadline = deadline

    def add_contribution(self, amount):
        self.current_amount += float(amount)

    def progress_pct(self):
        if self.target_amount == 0:
            return 0
        return min(100, (self.current_amount / self.target_amount) * 100)

    def to_dict(self):
        return {
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "deadline": self.deadline,
        }

    @staticmethod
    def from_dict(d):
        g = SavingsGoal.__new__(SavingsGoal)
        g.__dict__.update(d)
        return g


# ──────────────────────────────────────────────
# CORE SYSTEM
# ──────────────────────────────────────────────

class FinanceManager:
    DATA_FILE = "sfm_data.json"

    def __init__(self):
        self.transactions: list[Transaction] = []
        self.budgets: dict[str, Budget] = {}
        self.goals: list[SavingsGoal] = []
        self._load()

    # ── Persistence ────────────────────────────
    def _load(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE) as f:
                data = json.load(f)
            self.transactions = [Transaction.from_dict(t) for t in data.get("transactions", [])]
            self.budgets = {k: Budget(v["category"], v["monthly_limit"])
                            for k, v in data.get("budgets", {}).items()}
            self.goals = [SavingsGoal.from_dict(g) for g in data.get("goals", [])]

    def save(self):
        with open(self.DATA_FILE, "w") as f:
            json.dump({
                "transactions": [t.to_dict() for t in self.transactions],
                "budgets": {k: v.to_dict() for k, v in self.budgets.items()},
                "goals": [g.to_dict() for g in self.goals],
            }, f, indent=2)

    # ── Transactions ───────────────────────────
    def add_transaction(self, amount, category, description,
                        date=None, trans_type="expense", tag=None):
        t = Transaction(amount, category, description, date, trans_type, tag)
        # Auto-detect subscriptions
        if any(kw in description.lower() for kw in SUBSCRIPTION_KEYWORDS):
            t.tag = "subscription"
        self.transactions.append(t)
        self.save()
        print(f"  ✔ Added [{trans_type.upper()}] ₹{amount:,.2f} – {description}")
        return t

    def delete_transaction(self, trans_id):
        before = len(self.transactions)
        self.transactions = [t for t in self.transactions if t.id != trans_id]
        self.save()
        return len(self.transactions) < before

    def get_dataframe(self) -> pd.DataFrame:
        if not self.transactions:
            return pd.DataFrame(columns=["id","amount","category","description",
                                         "date","type","tag"])
        df = pd.DataFrame([t.to_dict() for t in self.transactions])
        df["date"] = pd.to_datetime(df["date"])
        df["amount"] = df["amount"].astype(float)
        return df

    # ── Summary ────────────────────────────────
    def monthly_summary(self, year=None, month=None):
        now = datetime.now()
        year = year or now.year
        month = month or now.month
        df = self.get_dataframe()
        if df.empty:
            return {}
        mask = (df["date"].dt.year == year) & (df["date"].dt.month == month)
        mdf = df[mask]
        income = mdf[mdf["type"] == "income"]["amount"].sum()
        expenses = mdf[mdf["type"] == "expense"]["amount"].sum()
        by_cat = (mdf[mdf["type"] == "expense"]
                  .groupby("category")["amount"].sum()
                  .sort_values(ascending=False))
        return {
            "year": year, "month": month,
            "income": income, "expenses": expenses,
            "net": income - expenses,
            "by_category": by_cat.to_dict(),
            "transactions_count": len(mdf),
        }

    # ── Budget ─────────────────────────────────
    def set_budget(self, category, monthly_limit):
        self.budgets[category] = Budget(category, monthly_limit)
        self.save()
        print(f"  ✔ Budget set: {category} → ₹{monthly_limit:,.2f}/month")

    def budget_status(self):
        summary = self.monthly_summary()
        by_cat = summary.get("by_category", {})
        rows = []
        for cat, b in self.budgets.items():
            spent = by_cat.get(cat, 0)
            pct = (spent / b.monthly_limit * 100) if b.monthly_limit else 0
            status = "🔴 OVER" if pct > 100 else ("🟡 WARN" if pct > 80 else "🟢 OK")
            rows.append({
                "Category": cat,
                "Budget": b.monthly_limit,
                "Spent": spent,
                "Remaining": b.monthly_limit - spent,
                "% Used": round(pct, 1),
                "Status": status,
            })
        return pd.DataFrame(rows)

    # ── Anomaly Detection ──────────────────────
    def detect_anomalies(self, z_threshold=2.0):
        df = self.get_dataframe()
        if df.empty or len(df) < 5:
            return pd.DataFrame()
        expenses = df[df["type"] == "expense"].copy()
        if expenses.empty:
            return pd.DataFrame()
        mean = expenses["amount"].mean()
        std = expenses["amount"].std()
        if std == 0:
            return pd.DataFrame()
        expenses["z_score"] = (expenses["amount"] - mean) / std
        anomalies = expenses[expenses["z_score"].abs() > z_threshold]
        return anomalies[["date", "description", "category", "amount", "z_score"]]

    # ── Subscription Detector ──────────────────
    def get_subscriptions(self):
        df = self.get_dataframe()
        if df.empty:
            return pd.DataFrame()
        subs = df[(df["tag"] == "subscription") | (df["type"] == "expense")].copy()
        subs = subs[subs["description"].str.lower().apply(
            lambda d: any(kw in d for kw in SUBSCRIPTION_KEYWORDS))]
        return subs[["date", "description", "category", "amount"]].drop_duplicates(
            subset=["description"])

    # ── Expense Prediction ─────────────────────
    def predict_next_month(self):
        df = self.get_dataframe()
        if df.empty:
            return {}
        expenses = df[df["type"] == "expense"].copy()
        if expenses.empty:
            return {}
        expenses["month"] = expenses["date"].dt.to_period("M")
        monthly = expenses.groupby("month")["amount"].sum().reset_index()
        monthly["amount"] = monthly["amount"].astype(float)

        if len(monthly) < 2:
            return {"predicted": float(monthly["amount"].mean()), "method": "average"}

        # Linear regression via numpy
        y = monthly["amount"].values
        x = np.arange(len(y))
        coeffs = np.polyfit(x, y, 1)
        predicted = float(np.polyval(coeffs, len(y)))

        # Category-level prediction
        cat_monthly = (expenses.groupby(["month", "category"])["amount"]
                       .sum().reset_index())
        cat_pred = {}
        for cat in cat_monthly["category"].unique():
            cat_data = cat_monthly[cat_monthly["category"] == cat]["amount"].values
            if len(cat_data) >= 2:
                xc = np.arange(len(cat_data))
                cc = np.polyfit(xc, cat_data, 1)
                cat_pred[cat] = max(0, float(np.polyval(cc, len(cat_data))))
            else:
                cat_pred[cat] = float(cat_data.mean())

        return {
            "predicted_total": max(0, predicted),
            "predicted_by_category": cat_pred,
            "method": "linear_regression",
            "history_months": len(monthly),
        }

    # ── Savings Goals ──────────────────────────
    def add_goal(self, name, target, deadline):
        self.goals.append(SavingsGoal(name, target, deadline))
        self.save()
        print(f"  ✔ Goal added: {name} – ₹{target:,.2f} by {deadline}")

    def contribute_to_goal(self, name, amount):
        for g in self.goals:
            if g.name.lower() == name.lower():
                g.add_contribution(amount)
                self.save()
                print(f"  ✔ Contributed ₹{amount:,.2f} to '{name}' "
                      f"({g.progress_pct():.1f}% complete)")
                return
        print(f"  ✗ Goal '{name}' not found.")

    # ── Visualizations ─────────────────────────
    def generate_report(self, output_path="finance_report.png"):
        df = self.get_dataframe()
        if df.empty:
            print("  ✗ No data to visualize.")
            return

        # ── palette ──────────────────────────────
        BG        = "#0D0F14"
        PANEL     = "#161B24"
        ACCENT    = "#00E5C3"
        ACCENT2   = "#FF6B6B"
        ACCENT3   = "#FFD93D"
        TEXT      = "#E8EAF0"
        SUBTEXT   = "#6B7280"
        GRID      = "#1F2937"

        COLORS = ["#00E5C3","#FF6B6B","#FFD93D","#A78BFA","#34D399",
                  "#FB923C","#60A5FA","#F472B6","#4ADE80","#FACC15",
                  "#818CF8","#F87171","#2DD4BF"]

        fig = plt.figure(figsize=(20, 14), facecolor=BG)
        fig.suptitle("Smart Finance Manager — Dashboard",
                     color=TEXT, fontsize=22, fontweight="bold", y=0.97)
        gs = GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.35,
                      left=0.05, right=0.97, top=0.92, bottom=0.06)

        def _style_ax(ax):
            ax.set_facecolor(PANEL)
            ax.tick_params(colors=SUBTEXT, labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor(GRID)
            ax.grid(color=GRID, linestyle="--", linewidth=0.5, alpha=0.6)

        # 1. Monthly Income vs Expense
        ax1 = fig.add_subplot(gs[0, :2])
        _style_ax(ax1)
        expenses_m = df[df["type"]=="expense"].copy()
        income_m   = df[df["type"]=="income"].copy()
        expenses_m["month"] = expenses_m["date"].dt.to_period("M").astype(str)
        income_m["month"]   = income_m["date"].dt.to_period("M").astype(str)
        exp_grp = expenses_m.groupby("month")["amount"].sum()
        inc_grp = income_m.groupby("month")["amount"].sum()
        months = sorted(set(list(exp_grp.index) + list(inc_grp.index)))
        x = np.arange(len(months))
        w = 0.35
        ax1.bar(x - w/2, [inc_grp.get(m, 0) for m in months],
                width=w, color=ACCENT, alpha=0.85, label="Income")
        ax1.bar(x + w/2, [exp_grp.get(m, 0) for m in months],
                width=w, color=ACCENT2, alpha=0.85, label="Expense")
        ax1.set_xticks(x); ax1.set_xticklabels(months, rotation=30, ha="right")
        ax1.set_title("Monthly Income vs Expenses", color=TEXT, fontsize=11, pad=8)
        ax1.legend(facecolor=PANEL, labelcolor=TEXT, fontsize=8, framealpha=0.5)
        ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:,.0f}"))
        ax1.set_ylabel("Amount (₹)", color=SUBTEXT, fontsize=8)

        # 2. Category Pie
        ax2 = fig.add_subplot(gs[0, 2:])
        ax2.set_facecolor(PANEL)
        cat_data = (df[df["type"]=="expense"]
                    .groupby("category")["amount"].sum()
                    .sort_values(ascending=False).head(8))
        if not cat_data.empty:
            wedges, texts, autotexts = ax2.pie(
                cat_data.values,
                labels=cat_data.index,
                autopct="%1.1f%%",
                colors=COLORS[:len(cat_data)],
                pctdistance=0.8,
                startangle=140,
                wedgeprops={"linewidth": 1.5, "edgecolor": BG},
            )
            for t in texts: t.set_color(TEXT); t.set_fontsize(7)
            for at in autotexts: at.set_color(BG); at.set_fontsize(7); at.set_fontweight("bold")
        ax2.set_title("Expense by Category", color=TEXT, fontsize=11, pad=8)

        # 3. Daily Spending Line
        ax3 = fig.add_subplot(gs[1, :2])
        _style_ax(ax3)
        daily = (df[df["type"]=="expense"]
                 .groupby(df["date"].dt.date)["amount"].sum()
                 .reset_index())
        daily.columns = ["date","amount"]
        daily["date"] = pd.to_datetime(daily["date"])
        daily = daily.sort_values("date")
        ax3.fill_between(daily["date"], daily["amount"],
                         alpha=0.3, color=ACCENT)
        ax3.plot(daily["date"], daily["amount"],
                 color=ACCENT, linewidth=1.8)
        # 7-day rolling avg
        if len(daily) >= 7:
            roll = daily["amount"].rolling(7).mean()
            ax3.plot(daily["date"], roll, color=ACCENT3,
                     linewidth=1.5, linestyle="--", label="7-day avg")
            ax3.legend(facecolor=PANEL, labelcolor=TEXT, fontsize=8, framealpha=0.5)
        ax3.set_title("Daily Expense Trend", color=TEXT, fontsize=11, pad=8)
        ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:,.0f}"))
        fig.autofmt_xdate(rotation=30)

        # 4. Budget Utilisation
        ax4 = fig.add_subplot(gs[1, 2:])
        _style_ax(ax4)
        bdf = self.budget_status()
        if not bdf.empty:
            pcts = bdf["% Used"].values
            cats = bdf["Category"].values
            colors_b = [ACCENT2 if p > 100 else (ACCENT3 if p > 80 else ACCENT)
                        for p in pcts]
            bars = ax4.barh(cats, pcts, color=colors_b, alpha=0.85)
            ax4.axvline(100, color=ACCENT2, linewidth=1.5, linestyle="--")
            ax4.set_xlabel("% of Budget Used", color=SUBTEXT, fontsize=8)
            ax4.set_xlim(0, max(130, max(pcts) + 20))
            for bar, pct in zip(bars, pcts):
                ax4.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                         f"{pct:.0f}%", va="center", color=TEXT, fontsize=7)
        ax4.set_title("Budget Utilisation", color=TEXT, fontsize=11, pad=8)

        # 5. Top Expenses
        ax5 = fig.add_subplot(gs[2, :2])
        _style_ax(ax5)
        top = (df[df["type"]=="expense"]
               .nlargest(10, "amount")[["description","amount"]])
        top["short"] = top["description"].str[:20]
        ax5.barh(top["short"][::-1], top["amount"][::-1],
                 color=COLORS[:10][::-1], alpha=0.85)
        ax5.set_title("Top 10 Expenses", color=TEXT, fontsize=11, pad=8)
        ax5.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:,.0f}"))
        ax5.set_xlabel("Amount (₹)", color=SUBTEXT, fontsize=8)

        # 6. Savings Goals
        ax6 = fig.add_subplot(gs[2, 2:])
        _style_ax(ax6)
        if self.goals:
            goal_names = [g.name[:18] for g in self.goals]
            progresses = [g.progress_pct() for g in self.goals]
            targets    = [g.target_amount for g in self.goals]
            currents   = [g.current_amount for g in self.goals]
            x6 = np.arange(len(goal_names))
            ax6.bar(x6, targets, color=GRID, label="Target", alpha=0.8)
            ax6.bar(x6, currents, color=ACCENT, label="Saved", alpha=0.9)
            ax6.set_xticks(x6); ax6.set_xticklabels(goal_names, rotation=20, ha="right")
            for i, (p, c) in enumerate(zip(progresses, currents)):
                ax6.text(i, c + targets[i]*0.02,
                         f"{p:.0f}%", ha="center", color=TEXT, fontsize=8, fontweight="bold")
            ax6.legend(facecolor=PANEL, labelcolor=TEXT, fontsize=8, framealpha=0.5)
            ax6.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"₹{v:,.0f}"))
        else:
            ax6.text(0.5, 0.5, "No savings goals set",
                     ha="center", va="center", color=SUBTEXT, transform=ax6.transAxes)
        ax6.set_title("Savings Goals Progress", color=TEXT, fontsize=11, pad=8)

        plt.savefig(output_path, dpi=130, bbox_inches="tight", facecolor=BG)
        print(f"  ✔ Report saved → {output_path}")
        return output_path


# ──────────────────────────────────────────────
# DEMO SEED DATA
# ──────────────────────────────────────────────

def seed_demo_data(fm: FinanceManager):
    """Populate with realistic 3-month demo data."""
    print("\n📦 Seeding demo data...")
    today = datetime.now()

    def d(days_ago): return (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    # Income
    for i in [0, 31, 62]:
        fm.add_transaction(55000, "Income", "Monthly Salary",      date=d(i), trans_type="income")
    fm.add_transaction(8000, "Income", "Freelance Project",        date=d(10), trans_type="income")
    fm.add_transaction(3000, "Income", "Interest Income",          date=d(20), trans_type="income")

    # Housing
    fm.add_transaction(12000, "Housing", "Rent - October",         date=d(5))
    fm.add_transaction(12000, "Housing", "Rent - September",       date=d(36))
    fm.add_transaction(12000, "Housing", "Rent - August",          date=d(67))
    fm.add_transaction(2400,  "Utilities", "Electricity Bill",     date=d(8))
    fm.add_transaction(800,   "Utilities", "Water Bill",           date=d(8))
    fm.add_transaction(1200,  "Utilities", "Internet Plan",        date=d(9))

    # Food
    for day, amt, desc in [
        (1,450,"Zomato Order"),(3,320,"Grocery Store"),(5,180,"Coffee Shop"),
        (7,600,"Restaurant Dinner"),(9,290,"Grocery Store"),(11,150,"Lunch"),
        (14,480,"Weekend Brunch"),(16,210,"Grocery Store"),(18,130,"Snacks"),
        (21,550,"Family Dinner"),(23,380,"Grocery Store"),(25,200,"Cafe"),
        (28,420,"Zomato Order"),(31,300,"Grocery Store"),(35,250,"Lunch"),
        (40,680,"Restaurant"),(45,340,"Grocery Store"),(50,190,"Coffee Shop"),
        (55,420,"Zomato Order"),(60,310,"Grocery Store"),(65,170,"Snacks"),
    ]:
        fm.add_transaction(amt, "Food & Dining", desc, date=d(day))

    # Transport
    for day, amt, desc in [
        (2,1200,"Petrol"),(6,150,"Ola Ride"),(10,80,"Auto Ride"),
        (13,1300,"Petrol"),(19,200,"Rapido"),(24,95,"Bus Pass"),
        (33,1150,"Petrol"),(38,180,"Ola Ride"),(42,1200,"Petrol"),
        (48,160,"Auto Ride"),(53,1100,"Petrol"),(58,200,"Ola Ride"),
    ]:
        fm.add_transaction(amt, "Transportation", desc, date=d(day))

    # Entertainment / Subscriptions
    for day, amt, desc in [
        (1,649,"Netflix Subscription"),(1,199,"Spotify Premium"),
        (2,1299,"Amazon Prime"),(15,500,"Movie Theatre"),(22,300,"Gaming Top-up"),
        (32,649,"Netflix Subscription"),(32,199,"Spotify Premium"),
        (63,649,"Netflix Subscription"),(63,199,"Spotify Premium"),
    ]:
        fm.add_transaction(amt, "Entertainment", desc, date=d(day))

    # Shopping
    for day, amt, desc in [
        (4,2500,"Myntra Clothes"),(12,800,"Pharmacy"),(20,3200,"New Shoes"),
        (27,600,"Books"),(34,4500,"Electronics - Earphones"),(41,1200,"Household Items"),
        (48,700,"Stationery"),(55,2800,"Clothing"),(62,950,"Personal Care"),
    ]:
        fm.add_transaction(amt, "Shopping", desc, date=d(day))

    # Healthcare
    fm.add_transaction(1500, "Healthcare", "Doctor Visit",          date=d(16))
    fm.add_transaction(850,  "Healthcare", "Pharmacy",              date=d(16))
    fm.add_transaction(2000, "Healthcare", "Lab Tests",             date=d(44))

    # Anomalous large transaction
    fm.add_transaction(25000, "Shopping", "Laptop Repair — Emergency", date=d(3))

    # Education
    fm.add_transaction(3500, "Education", "Online Course - Udemy",  date=d(10))
    fm.add_transaction(2000, "Education", "Books & Stationery",     date=d(25))

    # Budgets
    budgets = {
        "Food & Dining": 6000, "Transportation": 3000, "Housing": 14000,
        "Healthcare": 2000, "Entertainment": 2000, "Shopping": 5000,
        "Utilities": 4500, "Education": 3000, "Subscriptions": 2000,
    }
    for cat, limit in budgets.items():
        fm.set_budget(cat, limit)

    # Savings Goals
    fm.add_goal("Emergency Fund", 100000, "2025-12-31")
    fm.add_goal("Vacation to Goa", 30000, "2025-06-01")
    fm.add_goal("New Laptop",      60000, "2025-09-01")

    fm.contribute_to_goal("Emergency Fund", 15000)
    fm.contribute_to_goal("Emergency Fund", 8000)
    fm.contribute_to_goal("Vacation to Goa", 12000)
    fm.contribute_to_goal("New Laptop", 5000)

    print("✅ Demo data seeded successfully!\n")


# ──────────────────────────────────────────────
# CONSOLE INTERFACE
# ──────────────────────────────────────────────

def print_header():
    print("""
╔══════════════════════════════════════════════════════════════╗
║   Smart Finance Manager & Personal Expense Intelligence      ║
║                       SFM-PEIS v1.0                          ║
╚══════════════════════════════════════════════════════════════╝
""")

def print_menu():
    print("""
┌─────────────────────────────────────────┐
│              MAIN MENU                  │
├─────────────────────────────────────────┤
│  1. Add Transaction                     │
│  2. View Monthly Summary                │
│  3. Budget Status                       │
│  4. Detect Anomalies                    │
│  5. View Subscriptions                  │
│  6. Predict Next Month Expenses         │
│  7. Manage Savings Goals                │
│  8. Generate Visual Report              │
│  9. Seed Demo Data                      │
│  0. Exit                                │
└─────────────────────────────────────────┘
""")

def run_cli():
    fm = FinanceManager()
    print_header()

    while True:
        print_menu()
        choice = input("Enter choice: ").strip()

        if choice == "1":
            print("\n── Add Transaction ──")
            amount = float(input("Amount (₹): "))
            print("Categories:", ", ".join(CATEGORIES))
            category = input("Category: ").strip()
            description = input("Description: ").strip()
            date = input("Date (YYYY-MM-DD, blank=today): ").strip() or None
            ttype = input("Type (expense/income) [expense]: ").strip() or "expense"
            fm.add_transaction(amount, category, description, date, ttype)

        elif choice == "2":
            s = fm.monthly_summary()
            print(f"\n── Monthly Summary ({s.get('month','-')}/{s.get('year','-')}) ──")
            print(f"  Income   : ₹{s.get('income',0):,.2f}")
            print(f"  Expenses : ₹{s.get('expenses',0):,.2f}")
            print(f"  Net      : ₹{s.get('net',0):,.2f}")
            print("\n  By Category:")
            for cat, amt in s.get("by_category", {}).items():
                print(f"    {cat:<25} ₹{amt:>10,.2f}")

        elif choice == "3":
            bdf = fm.budget_status()
            if bdf.empty:
                print("\n  No budgets set.")
            else:
                print("\n── Budget Status ──\n")
                print(bdf.to_string(index=False))

        elif choice == "4":
            adf = fm.detect_anomalies()
            if adf.empty:
                print("\n  ✓ No anomalies detected.")
            else:
                print(f"\n── Anomalies Detected ({len(adf)}) ──\n")
                print(adf.to_string(index=False))

        elif choice == "5":
            sdf = fm.get_subscriptions()
            if sdf.empty:
                print("\n  No subscriptions detected.")
            else:
                total = sdf["amount"].sum()
                print(f"\n── Active Subscriptions ── (Total: ₹{total:,.2f}/mo)\n")
                print(sdf.to_string(index=False))

        elif choice == "6":
            pred = fm.predict_next_month()
            if not pred:
                print("\n  Not enough data for prediction.")
            else:
                print(f"\n── Next Month Prediction ({pred.get('method')}) ──")
                print(f"  Predicted Total : ₹{pred.get('predicted_total',0):,.2f}")
                print("\n  By Category:")
                for cat, amt in sorted(pred.get("predicted_by_category",{}).items(),
                                        key=lambda x:-x[1]):
                    print(f"    {cat:<25} ₹{amt:>10,.2f}")

        elif choice == "7":
            print("\n── Savings Goals ──")
            for g in fm.goals:
                bar = "█" * int(g.progress_pct()//5) + "░" * (20 - int(g.progress_pct()//5))
                print(f"  {g.name:<25} [{bar}] {g.progress_pct():5.1f}%  "
                      f"₹{g.current_amount:,.0f} / ₹{g.target_amount:,.0f}")
            print("\n  a) Add Goal   b) Contribute   q) Back")
            sub = input("  Choice: ").strip()
            if sub == "a":
                name   = input("  Goal name: ")
                target = float(input("  Target amount: "))
                dl     = input("  Deadline (YYYY-MM-DD): ")
                fm.add_goal(name, target, dl)
            elif sub == "b":
                name   = input("  Goal name: ")
                amount = float(input("  Amount: "))
                fm.contribute_to_goal(name, amount)

        elif choice == "8":
            path = fm.generate_report("finance_report.png")
            print(f"\n  Chart saved to: {path}")

        elif choice == "9":
            if os.path.exists(fm.DATA_FILE):
                yn = input("  This will clear existing data. Continue? (y/n): ")
                if yn.lower() != "y":
                    continue
                fm.transactions = []; fm.budgets = {}; fm.goals = []
            seed_demo_data(fm)

        elif choice == "0":
            print("\n  👋 Goodbye!\n")
            break
        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    run_cli()
