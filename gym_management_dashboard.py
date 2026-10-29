import csv
import os
from datetime import datetime
from collections import defaultdict

# Matplotlib is used for charts. The program can still run if it is unavailable.
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False


# Store CSV files beside this Python script.
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

MEMBER_FILE = os.path.join(BASE_DIR, "members.csv")
TRAINER_FILE = os.path.join(BASE_DIR, "trainers.csv")
PLAN_FILE = os.path.join(BASE_DIR, "membership_plans.csv")
PAYMENT_FILE = os.path.join(BASE_DIR, "payments.csv")


# ==========================================
# INPUT VALIDATION
# ==========================================

def get_text(message):
    while True:
        value = input(message).strip()

        if not value:
            print("This field cannot be empty.")
        elif "|" in value:
            print("Please do not enter the | character.")
        else:
            return value


def get_integer(message, minimum=0):
    while True:
        try:
            value = int(input(message).strip())

            if value < minimum:
                print("Enter a whole number greater than or equal to", minimum)
            else:
                return value
        except ValueError:
            print("Please enter a valid whole number.")


def get_amount(message, allow_zero=False):
    while True:
        try:
            value = float(input(message).strip())
            if value < 0 or (value == 0 and not allow_zero):
                print("Enter a valid amount greater than zero.")
            else:
                return round(value, 2)
        except ValueError:
            print("Please enter a valid amount.")


# ==========================================
# CSV FILE HELPERS
# ==========================================

def ensure_csv_files():
    headers = {
        MEMBER_FILE: [
            "member_id", "name", "age", "gender", "phone",
            "trainer_id", "plan_id", "date_added"
        ],
        TRAINER_FILE: [
            "trainer_id", "name", "specialization", "experience"
        ],
        PLAN_FILE: [
            "plan_id", "name", "duration_months", "fee"
        ],
        PAYMENT_FILE: [
            "payment_id", "member_id", "amount", "status", "date_time"
        ]
    }

    for filename, columns in headers.items():
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            with open(filename, "w", newline="", encoding="utf-8") as file:
                csv.writer(file).writerow(columns)


def read_rows(filename):
    ensure_csv_files()
    with open(filename, "r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def write_rows(filename, headers, rows):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def append_row(filename, headers, row):
    ensure_csv_files()
    with open(filename, "a", newline="", encoding="utf-8") as file:
        csv.DictWriter(file, fieldnames=headers).writerow(row)


# ==========================================
# CLASSES
# ==========================================

class Member:
    def __init__(self, member_id, name, age, gender, phone,
                 trainer_id="", plan_id="", date_added=""):
        self.member_id = member_id
        self.name = name
        self.age = age
        self.gender = gender
        self.phone = phone
        self.trainer_id = trainer_id
        self.plan_id = plan_id
        self.date_added = date_added

    def display(self, trainers=None, plans=None):
        trainer_name = "Not assigned"
        plan_name = "No plan assigned"

        if trainers and self.trainer_id in trainers:
            trainer_name = trainers[self.trainer_id]["name"]
        if plans and self.plan_id in plans:
            plan_name = plans[self.plan_id]["name"]

        print("\nMember ID:", self.member_id)
        print("Name:", self.name)
        print("Age:", self.age)
        print("Gender:", self.gender)
        print("Phone:", self.phone)
        print("Trainer:", trainer_name)
        print("Membership Plan:", plan_name)
        print("Date Added:", self.date_added or "Not recorded")


class Trainer:
    def __init__(self, trainer_id, name, specialization, experience):
        self.trainer_id = trainer_id
        self.name = name
        self.specialization = specialization
        self.experience = experience

    def display(self):
        print("\nTrainer ID:", self.trainer_id)
        print("Name:", self.name)
        print("Specialization:", self.specialization)
        print("Experience:", self.experience, "years")


class MembershipPlan:
    def __init__(self, plan_id, name, duration_months, fee):
        self.plan_id = plan_id
        self.name = name
        self.duration_months = duration_months
        self.fee = fee

    def display(self):
        print("\nPlan ID:", self.plan_id)
        print("Plan Name:", self.name)
        print("Duration:", self.duration_months, "months")
        print("Fee: Rs.", format(self.fee, ".2f"))


# ==========================================
# GYM MANAGEMENT SYSTEM
# ==========================================

class Gym:
    def __init__(self):
        ensure_csv_files()

    # ---------- Data access helpers ----------

    def get_members(self):
        return read_rows(MEMBER_FILE)

    def get_trainers(self):
        return read_rows(TRAINER_FILE)

    def get_plans(self):
        return read_rows(PLAN_FILE)

    def get_payments(self):
        return read_rows(PAYMENT_FILE)

    def member_map(self):
        return {row["member_id"]: row for row in self.get_members()}

    def trainer_map(self):
        return {row["trainer_id"]: row for row in self.get_trainers()}

    def plan_map(self):
        return {row["plan_id"]: row for row in self.get_plans()}

    def next_id(self, filename, field, prefix, start):
        highest = start
        for row in read_rows(filename):
            try:
                current = row.get(field, "").replace(prefix, "")
                highest = max(highest, int(current))
            except (ValueError, AttributeError):
                continue
        return f"{prefix}{highest + 1}"

    # ======================================
    # MEMBER MANAGEMENT
    # ======================================

    def add_member(self):
        members = self.get_members()
        member_id = self.next_id(MEMBER_FILE, "member_id", "MEM-", 100)

        name = get_text("Enter member name: ")
        age = get_integer("Enter age: ", 1)
        gender = get_text("Enter gender: ")
        phone = get_text("Enter phone number: ")

        row = {
            "member_id": member_id,
            "name": name,
            "age": age,
            "gender": gender,
            "phone": phone,
            "trainer_id": "",
            "plan_id": "",
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        append_row(MEMBER_FILE, [
            "member_id", "name", "age", "gender", "phone",
            "trainer_id", "plan_id", "date_added"
        ], row)

        print("\nMember added successfully.")
        print("Member ID:", member_id)

    def view_members(self):
        members = self.get_members()
        trainers = self.trainer_map()
        plans = self.plan_map()

        if not members:
            print("No members found.")
            return

        print("\n========== ALL MEMBERS ==========")
        for row in members:
            member = Member(
                row["member_id"], row["name"], row["age"], row["gender"],
                row["phone"], row.get("trainer_id", ""),
                row.get("plan_id", ""), row.get("date_added", "")
            )
            member.display(trainers, plans)

    def search_member(self):
        member_id = input("Enter Member ID (e.g. MEM-101): ").strip().upper()
        member = self.member_map().get(member_id)

        if member:
            Member(
                member["member_id"], member["name"], member["age"],
                member["gender"], member["phone"],
                member.get("trainer_id", ""), member.get("plan_id", ""),
                member.get("date_added", "")
            ).display(self.trainer_map(), self.plan_map())
        else:
            print("Member not found.")

    def delete_member(self):
        member_id = input("Enter Member ID to delete: ").strip().upper()
        members = self.get_members()

        if not any(row["member_id"] == member_id for row in members):
            print("Member not found.")
            return

        remaining = [row for row in members if row["member_id"] != member_id]
        write_rows(MEMBER_FILE, [
            "member_id", "name", "age", "gender", "phone",
            "trainer_id", "plan_id", "date_added"
        ], remaining)

        # Keep payment history for audit purposes; it is not deleted.
        print("Member deleted successfully. Existing payment history was kept.")

    def member_menu(self):
        actions = {
            "1": self.add_member,
            "2": self.view_members,
            "3": self.search_member,
            "4": self.delete_member
        }

        while True:
            print("\n========== MEMBER MANAGEMENT ==========")
            print("1. Add Member")
            print("2. View Members")
            print("3. Search Member")
            print("4. Delete Member")
            print("5. Back")
            choice = input("Enter choice: ").strip()

            if choice == "5":
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Invalid choice.")

    # ======================================
    # TRAINER MANAGEMENT
    # ======================================

    def add_trainer(self):
        trainer_id = self.next_id(TRAINER_FILE, "trainer_id", "TR-", 100)
        name = get_text("Enter trainer name: ")
        specialization = get_text("Enter specialization: ")
        experience = get_integer("Enter experience in years: ", 0)

        append_row(TRAINER_FILE, [
            "trainer_id", "name", "specialization", "experience"
        ], {
            "trainer_id": trainer_id,
            "name": name,
            "specialization": specialization,
            "experience": experience
        })

        print("Trainer added successfully.")
        print("Trainer ID:", trainer_id)

    def view_trainers(self):
        trainers = self.get_trainers()
        if not trainers:
            print("No trainers found.")
            return

        print("\n========== ALL TRAINERS ==========")
        for row in trainers:
            Trainer(
                row["trainer_id"], row["name"],
                row["specialization"], row["experience"]
            ).display()

    def search_trainer(self):
        trainer_id = input("Enter Trainer ID (e.g. TR-101): ").strip().upper()
        trainer = self.trainer_map().get(trainer_id)

        if trainer:
            Trainer(
                trainer["trainer_id"], trainer["name"],
                trainer["specialization"], trainer["experience"]
            ).display()
        else:
            print("Trainer not found.")

    def assign_trainer(self):
        member_id = input("Enter Member ID: ").strip().upper()
        trainer_id = input("Enter Trainer ID: ").strip().upper()

        members = self.get_members()
        trainers = self.trainer_map()

        if member_id not in {row["member_id"] for row in members}:
            print("Member not found.")
            return
        if trainer_id not in trainers:
            print("Trainer not found.")
            return

        for row in members:
            if row["member_id"] == member_id:
                row["trainer_id"] = trainer_id

        write_rows(MEMBER_FILE, [
            "member_id", "name", "age", "gender", "phone",
            "trainer_id", "plan_id", "date_added"
        ], members)
        print("Trainer assigned successfully.")

    def trainer_menu(self):
        actions = {
            "1": self.add_trainer,
            "2": self.view_trainers,
            "3": self.search_trainer,
            "4": self.assign_trainer
        }

        while True:
            print("\n========== TRAINER MANAGEMENT ==========")
            print("1. Add Trainer")
            print("2. View Trainers")
            print("3. Search Trainer")
            print("4. Assign Trainer to Member")
            print("5. Back")
            choice = input("Enter choice: ").strip()

            if choice == "5":
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Invalid choice.")

    # ======================================
    # MEMBERSHIP PLANS
    # ======================================

    def add_plan(self):
        plan_id = self.next_id(PLAN_FILE, "plan_id", "PLAN-", 100)
        name = get_text("Enter plan name: ")
        duration = get_integer("Enter duration in months: ", 1)
        fee = get_amount("Enter plan fee (Rs.): ")

        append_row(PLAN_FILE, [
            "plan_id", "name", "duration_months", "fee"
        ], {
            "plan_id": plan_id,
            "name": name,
            "duration_months": duration,
            "fee": f"{fee:.2f}"
        })

        print("Membership plan added successfully.")
        print("Plan ID:", plan_id)

    def view_plans(self):
        plans = self.get_plans()
        if not plans:
            print("No plans found.")
            return

        print("\n========== MEMBERSHIP PLANS ==========")
        for row in plans:
            MembershipPlan(
                row["plan_id"], row["name"],
                row["duration_months"], float(row["fee"])
            ).display()

    def assign_plan(self):
        member_id = input("Enter Member ID: ").strip().upper()
        members = self.get_members()

        if not any(row["member_id"] == member_id for row in members):
            print("Member not found.")
            return

        self.view_plans()
        plan_id = input("Enter Plan ID to assign: ").strip().upper()
        if plan_id not in self.plan_map():
            print("Plan not found.")
            return

        for row in members:
            if row["member_id"] == member_id:
                row["plan_id"] = plan_id

        write_rows(MEMBER_FILE, [
            "member_id", "name", "age", "gender", "phone",
            "trainer_id", "plan_id", "date_added"
        ], members)
        print("Membership plan assigned successfully.")

    def membership_menu(self):
        actions = {
            "1": self.add_plan,
            "2": self.view_plans,
            "3": self.assign_plan
        }

        while True:
            print("\n========== MEMBERSHIP PLANS ==========")
            print("1. Add Membership Plan")
            print("2. View Membership Plans")
            print("3. Assign Plan to Member")
            print("4. Back")
            choice = input("Enter choice: ").strip()

            if choice == "4":
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Invalid choice.")

    # ======================================
    # PAYMENT MANAGEMENT
    # ======================================

    def record_payment(self):
        members = self.member_map()
        if not members:
            print("Add a member before recording a payment.")
            return

        member_id = input("Enter Member ID: ").strip().upper()
        if member_id not in members:
            print("Member not found.")
            return

        payment_id = self.next_id(PAYMENT_FILE, "payment_id", "PAY-", 1000)
        amount = get_amount("Enter amount (Rs.): ")

        while True:
            status = input("Payment status (Paid/Pending): ").strip().lower()
            if status in ("paid", "pending"):
                status = status.title()
                break
            print("Please enter Paid or Pending.")

        append_row(PAYMENT_FILE, [
            "payment_id", "member_id", "amount", "status", "date_time"
        ], {
            "payment_id": payment_id,
            "member_id": member_id,
            "amount": f"{amount:.2f}",
            "status": status,
            "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        print("Payment recorded successfully.")
        print("Payment ID:", payment_id)

    def view_payments(self):
        payments = self.get_payments()
        members = self.member_map()

        if not payments:
            print("No payment records found.")
            return

        print("\n========== PAYMENT HISTORY ==========")
        for row in payments:
            member = members.get(row["member_id"], {})
            print("\nPayment ID:", row["payment_id"])
            print("Member ID:", row["member_id"])
            print("Member Name:", member.get("name", "Deleted member"))
            print("Amount: Rs.", row["amount"])
            print("Status:", row["status"])
            print("Date:", row["date_time"])

    def payment_menu(self):
        actions = {
            "1": self.record_payment,
            "2": self.view_payments
        }

        while True:
            print("\n========== PAYMENT MANAGEMENT ==========")
            print("1. Record Payment")
            print("2. View Payment History")
            print("3. Back")
            choice = input("Enter choice: ").strip()

            if choice == "3":
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Invalid choice.")

    # ======================================
    # DASHBOARD AND DATA VISUALIZATION
    # ======================================

    def show_dashboard(self):
        members = self.get_members()
        trainers = self.get_trainers()
        plans = self.get_plans()
        payments = self.get_payments()

        paid_revenue = 0.0
        pending_amount = 0.0
        for payment in payments:
            try:
                amount = float(payment["amount"])
                if payment["status"].lower() == "paid":
                    paid_revenue += amount
                else:
                    pending_amount += amount
            except (ValueError, KeyError):
                continue

        print("\n========== GYM DASHBOARD ==========")
        print("Total Members:", len(members))
        print("Total Trainers:", len(trainers))
        print("Membership Plans:", len(plans))
        print("Payment Records:", len(payments))
        print("Paid Revenue: Rs.", format(paid_revenue, ".2f"))
        print("Pending Payments: Rs.", format(pending_amount, ".2f"))

        if not CHARTS_AVAILABLE:
            print("\nCharts need matplotlib, which is not installed in this environment.")
            print("The summary above is still available.")
            return

        # Count members assigned to each plan.
        plan_names = {row["plan_id"]: row["name"] for row in plans}
        member_plan_counts = defaultdict(int)
        for member in members:
            plan_id = member.get("plan_id", "")
            label = plan_names.get(plan_id, "No plan")
            member_plan_counts[label] += 1

        # Calculate paid and pending payment totals.
        status_totals = {"Paid": 0.0, "Pending": 0.0}
        for payment in payments:
            try:
                status = payment["status"].title()
                if status in status_totals:
                    status_totals[status] += float(payment["amount"])
            except (ValueError, KeyError):
                continue

        # Count members added by date.
        members_per_day = defaultdict(int)
        for member in members:
            date_added = member.get("date_added", "")
            if len(date_added) >= 10:
                members_per_day[date_added[:10]] += 1

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle("GYM MANAGEMENT SYSTEM DASHBOARD",
                     fontsize=15, fontweight="bold")

        if member_plan_counts:
            axes[0, 0].bar(
                list(member_plan_counts.keys()),
                list(member_plan_counts.values())
            )
        else:
            axes[0, 0].text(0.5, 0.5, "No member data",
                            ha="center", va="center",
                            transform=axes[0, 0].transAxes)
        axes[0, 0].set_title("Members by Membership Plan")
        axes[0, 0].set_ylabel("Members")
        axes[0, 0].tick_params(axis="x", labelrotation=25)

        axes[0, 1].bar(
            list(status_totals.keys()), list(status_totals.values())
        )
        axes[0, 1].set_title("Payment Status Totals")
        axes[0, 1].set_ylabel("Amount (Rs.)")

        if plans:
            axes[1, 0].bar(
                [row["name"] for row in plans],
                [float(row["fee"]) for row in plans]
            )
        else:
            axes[1, 0].text(0.5, 0.5, "No plan data",
                            ha="center", va="center",
                            transform=axes[1, 0].transAxes)
        axes[1, 0].set_title("Membership Plan Fees")
        axes[1, 0].set_ylabel("Fee (Rs.)")
        axes[1, 0].tick_params(axis="x", labelrotation=25)

        dates = sorted(members_per_day.keys())
        if dates:
            axes[1, 1].plot(
                dates, [members_per_day[date] for date in dates],
                marker="o"
            )
        else:
            axes[1, 1].text(0.5, 0.5, "No member date data",
                            ha="center", va="center",
                            transform=axes[1, 1].transAxes)
        axes[1, 1].set_title("Members Added by Date")
        axes[1, 1].set_ylabel("New members")
        axes[1, 1].tick_params(axis="x", labelrotation=25)

        fig.tight_layout(rect=[0, 0, 1, 0.94])
        dashboard_file = os.path.join(BASE_DIR, "gym_dashboard.png")
        fig.savefig(dashboard_file, dpi=150, bbox_inches="tight")
        plt.close(fig)

        print("\nDashboard image saved to:", dashboard_file)
        print("If your coding website supports file downloads, download gym_dashboard.png.")

    # ======================================
    # MAIN MENU
    # ======================================

    def main_menu(self):
        actions = {
            "1": self.member_menu,
            "2": self.trainer_menu,
            "3": self.membership_menu,
            "4": self.payment_menu,
            "5": self.show_dashboard
        }

        while True:
            print("\n" + "=" * 45)
            print("       GYM MANAGEMENT SYSTEM")
            print("=" * 45)
            print("1. Member Management")
            print("2. Trainer Management")
            print("3. Membership Plans")
            print("4. Payment Management")
            print("5. Dashboard and Data Visualization")
            print("6. Exit")

            choice = input("Enter choice (1-6): ").strip()

            if choice == "6":
                print("Your data is saved in the CSV files. Thank you!")
                break

            action = actions.get(choice)
            if action is None:
                print("Invalid choice. Enter a number from 1 to 6.")
                continue

            try:
                action()
            except (EOFError, KeyboardInterrupt):
                print("\nProgram stopped.")
                break
            except Exception as error:
                print("Something went wrong:", type(error).__name__, error)

            input("\nPress Enter to return to the main menu...")


# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":
    gym = Gym()
    gym.main_menu()
