from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_apscheduler import APScheduler
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
from models import db, User, DailyBalance, BankInterest, AccountPayables, AccountReceivables, ProductionMain, ProductionSponge, SalesData, GasPlantData, ScrapData, OperationalData
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- CLI Command to Seed ALL Users ---
@app.cli.command("create-users")
def create_users():
    """Creates default users for all departments."""
    db.create_all()
    
    users_data = [
        {'user': 'Admin', 'pass': 'qwertqweQ#1', 'role': 'viewer', 'email': 'it@smlzim.com'},
        {'user': 'MD', 'pass': 'Kalpesh#1', 'role': 'viewer', 'email': 'kalpesh.p@smlzim.com'},
        {'user': 'MrUpendra', 'pass': '@upendra2026', 'role': 'viewer', 'email': 'upendra.a@smlzim.com'},
        {'user': 'MrLewis', 'pass': '@lewis#2026', 'role': 'viewer', 'email': 'lewis.k@smlzim.com'},
        {'user': 'MrJulius', 'pass': '@Julius!2026', 'role': 'viewer', 'email': 'julius.t@smlzim.com'},
        {'user': 'Simba.m', 'pass': '@simba$2026', 'role': 'uploader_balance', 'email': 'simba.m@smlzim.com'},
        {'user': 'Edith.d', 'pass': '@edith&2026', 'role': 'uploader_interest', 'email': 'edith.d@smlzim.com'},
        {'user': 'Placcidia.c', 'pass': '@placcidia#26', 'role': 'uploader_payables', 'email': 'placcidia.c@smlzim.com'},
        {'user': 'Aisha.p', 'pass': '@aisha#2026', 'role': 'uploader_receivables', 'email': 'aisha.p@smlzim.com'},
        # Consolidated Plant Manager
        {'user': 'Raviro.r', 'pass': '@raviro@2026', 'role': 'uploader_plant', 'email': 'raviro.r@smlzim.com'},
        {'user': 'MrMehta', 'pass': 'mehta@2026', 'role': 'uploader_sponge', 'email': 'mehta.b@smlzim.com'},
        {'user': 'Tinashe.m', 'pass': 'tinashe.m#2026', 'role': 'uploader_sales', 'email': 'tinashe.m@smlzim.com'},
        {'user': 'MrSatish', 'pass': 'satish.k@2026', 'role': 'uploader_scrap', 'email': 'satish.k@smlzim.com'},
    ]

    for u in users_data:
        if not User.query.filter_by(username=u['user']).first():
            new_user = User(
                username=u['user'], 
                email=u['email'],
                password=generate_password_hash(u['pass']), 
                role=u['role']
            )
            db.session.add(new_user)
            print(f"Created user: {u['user']}")
    
    db.session.commit()
    print("All users setup complete.")


# --- Routes ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'viewer':
            return redirect(url_for('dashboard'))
        return redirect(url_for('upload_data'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    
    # 1. Bank Balances
    balances = DailyBalance.query.filter_by(date=today).all()
    banks = ['CBZ Bank', 'Ecobank', 'Stanbic Bank', 'Nedbank']
    balance_map = {b.bank_name: b for b in balances}
    display_balances = []
    for bank in banks:
        entry = balance_map.get(bank)
        display_balances.append({
            'name': bank,
            'usd': entry.usd_balance if entry else 0.0,
            'zig': entry.zig_balance if entry else 0.0
        })

    # 2. Financial KPIs
    interest = BankInterest.query.order_by(BankInterest.date.desc()).first()
    int_data = {'total': (interest.paid + interest.due) if interest else 0.0, 'paid': interest.paid if interest else 0.0, 'due': interest.due if interest else 0.0}

    payables = AccountPayables.query.order_by(AccountPayables.date.desc()).first()
    pay_data = {'total': (payables.creditors + payables.creditors_project) if payables else 0.0, 'creditors': payables.creditors if payables else 0.0, 'project': payables.creditors_project if payables else 0.0}

    receivables = AccountReceivables.query.order_by(AccountReceivables.date.desc()).first()
    rec_data = {'total': receivables.total_amount if receivables else 0.0}

    # 3. Production Data
    prod_main = ProductionMain.query.order_by(ProductionMain.date.desc()).first()
    prod_sponge = ProductionSponge.query.order_by(ProductionSponge.date.desc()).first()
    total_billets = (prod_main.unit_1_cumulative + prod_main.unit_2_cumulative) if prod_main else 0.0

    # 4. Sales Data
    sales = SalesData.query.order_by(SalesData.date.desc()).first()
    total_sales_main = (sales.tmt_sales + sales.non_tmt_sales) if sales else 0.0

    # 5. Other KPIs
    gas = GasPlantData.query.order_by(GasPlantData.date.desc()).first()
    scrap = ScrapData.query.order_by(ScrapData.date.desc()).first()
    ops = OperationalData.query.order_by(OperationalData.date.desc()).first()
                           
    return render_template('dashboard.html', 
                           date=today, 
                           balances=display_balances,
                           interest=int_data,
                           payables=pay_data,
                           receivables=rec_data,
                           prod_main=prod_main,
                           prod_sponge=prod_sponge,
                           total_billets=total_billets,
                           sales=sales,
                           total_sales_main=total_sales_main,
                           gas=gas,
                           scrap=scrap,
                           ops=ops)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_data():
    if current_user.role == 'viewer':
        return redirect(url_for('dashboard'))

    today = date.today()
    role = current_user.role
    
    # --- DATE LOGIC ---
    effective_date = today 
    
    if role == 'uploader_interest':
        effective_date = today.replace(day=1) # 1st of Month
    elif role in ['uploader_payables', 'uploader_receivables']:
        days_since_monday = today.weekday() 
        effective_date = today - timedelta(days=days_since_monday) # Last Monday

    if request.method == 'POST':
        try:
            # 1. BANK BALANCES
            if role == 'uploader_balance':
                banks = ['CBZ Bank', 'Ecobank', 'Stanbic Bank', 'Nedbank']
                for bank in banks:
                    usd = float(request.form.get(f'{bank}_usd', 0))
                    zig = float(request.form.get(f'{bank}_zig', 0))
                    
                    entry = DailyBalance.query.filter_by(date=effective_date, bank_name=bank).first()
                    if entry:
                        entry.usd_balance = usd
                        entry.zig_balance = zig
                    else:
                        db.session.add(DailyBalance(date=effective_date, bank_name=bank, usd_balance=usd, zig_balance=zig))
            
            # 2. INTEREST
            elif role == 'uploader_interest':
                paid = float(request.form.get('int_paid', 0))
                due = float(request.form.get('int_due', 0))
                
                entry = BankInterest.query.filter_by(date=effective_date).first()
                if entry:
                    entry.paid = paid
                    entry.due = due
                else:
                    db.session.add(BankInterest(date=effective_date, paid=paid, due=due))

            # 3. PAYABLES
            elif role == 'uploader_payables':
                cred = float(request.form.get('pay_cred', 0))
                proj = float(request.form.get('pay_proj', 0))
                
                entry = AccountPayables.query.filter_by(date=effective_date).first()
                if entry:
                    entry.creditors = cred
                    entry.creditors_project = proj
                else:
                    db.session.add(AccountPayables(date=effective_date, creditors=cred, creditors_project=proj))

            # 4. RECEIVABLES
            elif role == 'uploader_receivables':
                total = float(request.form.get('rec_total', 0))
                
                entry = AccountReceivables.query.filter_by(date=effective_date).first()
                if entry:
                    entry.total_amount = total
                else:
                    db.session.add(AccountReceivables(date=effective_date, total_amount=total))

            # 5. SPONGE IRON
            elif role == 'uploader_sponge':
                produced = float(request.form.get('sponge_prod', 0))
                lost = float(request.form.get('sponge_lost', 0))
                
                entry = ProductionSponge.query.filter_by(date=today).first()
                if entry:
                    entry.produced_tns = produced
                    entry.lost_tns = lost
                else:
                    db.session.add(ProductionSponge(date=today, produced_tns=produced, lost_tns=lost))
                
            # 6. SALES KPI
            elif role == 'uploader_sales':
                angles = float(request.form.get('angles', 0))
                flats = float(request.form.get('flats', 0))
                window = float(request.form.get('window', 0))
                fencing = float(request.form.get('fencing', 0))
                channel = float(request.form.get('channel', 0))
                other = float(request.form.get('other', 0))
                
                redcliff = float(request.form.get('redcliff', 0))
                harare = float(request.form.get('harare', 0))
                mutare = float(request.form.get('mutare', 0))
                bulawayo = float(request.form.get('bulawayo', 0))
                chiredzi = float(request.form.get('chiredzi', 0))
                
                entry = SalesData.query.filter_by(date=today).first()
                if entry:
                    entry.angles_sales = angles
                    entry.flats_sales = flats
                    entry.window_sections_sales = window
                    entry.fencing_standard_sales = fencing
                    entry.channel_iron_sales = channel
                    entry.other_sections_sales = other
                    entry.redcliff_sales = redcliff
                    entry.harare_sales = harare
                    entry.mutare_sales = mutare
                    entry.bulawayo_sales = bulawayo
                    entry.chiredzi_sales = chiredzi
                else:
                    db.session.add(SalesData(
                        date=today,
                        angles_sales=angles, flats_sales=flats, window_sections_sales=window,
                        fencing_standard_sales=fencing, channel_iron_sales=channel, other_sections_sales=other,
                        redcliff_sales=redcliff, harare_sales=harare, mutare_sales=mutare, bulawayo_sales=bulawayo,chiredzi_sales=chiredzi
                    ))

            # 7. SCRAP UPLOADER
            elif role == 'uploader_scrap':
                supplied = float(request.form.get('supplied', 0))
                total = float(request.form.get('total', 0))
                
                entry = ScrapData.query.filter_by(date=today).first()
                if entry:
                    entry.supplied_tns = supplied
                    entry.total_purchased_tns = total
                else:
                    db.session.add(ScrapData(date=today, supplied_tns=supplied, total_purchased_tns=total))

            # 8. PLANT MANAGER (Production + Power + Gas)
            elif role == 'uploader_plant':
                # Production
                u1 = float(request.form.get('unit1', 0))
                u2 = float(request.form.get('unit2', 0))
                non_tmt = float(request.form.get('non_tmt', 0))
                tmt = float(request.form.get('tmt', 0))
                
                prod_entry = ProductionMain.query.filter_by(date=today).first()
                if prod_entry:
                    prod_entry.unit_1_cumulative = u1
                    prod_entry.unit_2_cumulative = u2
                    prod_entry.rolling_non_tmt = non_tmt
                    prod_entry.rolling_tmt = tmt
                else:
                    db.session.add(ProductionMain(date=today, unit_1_cumulative=u1, unit_2_cumulative=u2, rolling_non_tmt=non_tmt, rolling_tmt=tmt))

                # Power
                u1_h = int(request.form.get('u1_h', 0))
                u1_m = int(request.form.get('u1_m', 0))
                u2_h = int(request.form.get('u2_h', 0))
                u2_m = int(request.form.get('u2_m', 0))
                
                ops_entry = OperationalData.query.filter_by(date=today).first()
                if ops_entry:
                    ops_entry.u1_hours = u1_h
                    ops_entry.u1_minutes = u1_m
                    ops_entry.u2_hours = u2_h
                    ops_entry.u2_minutes = u2_m
                else:
                    db.session.add(OperationalData(date=today, u1_hours=u1_h, u1_minutes=u1_m, u2_hours=u2_h, u2_minutes=u2_m))

                # Gas
                gas_cyl = float(request.form.get('ind_gas', 0))
                gas_entry = GasPlantData.query.filter_by(date=today).first()
                if gas_entry:
                    gas_entry.industrial_gases_cyl = gas_cyl
                else:
                    db.session.add(GasPlantData(date=today, industrial_gases_cyl=gas_cyl))

            db.session.commit()
            flash(f'Data uploaded successfully for {effective_date.strftime("%d-%b-%Y")}', 'success')
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')

    return render_template('upload.html', role=role, date=effective_date)

# --- Email Schedulers ---

def send_email(to_email, subject, body):
    with app.app_context():
        try:
            if to_email:
                # 1. Get the CC string from Config
                cc_str = app.config.get('MAIL_CC')
                
                # 2. Convert comma-separated string to a List
                # This splits 'a@b.com, c@d.com' into ['a@b.com', 'c@d.com'] and removes spaces
                cc_list = [email.strip() for email in cc_str.split(',')] if cc_str else []
                
                # 3. Create Message
                msg = Message(subject, recipients=[to_email], cc=cc_list)
                msg.body = body
                
                # 4. Send
                mail.send(msg)
                print(f"Email sent to {to_email} (CC: {cc_list})")
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")

# Task 1: Reminder
@scheduler.task('cron', id='reminder_job', hour=8, minute=0)
def job_reminder():
    with app.app_context():
        uploaders = User.query.filter(User.role.like('uploader_%')).all()
        for u in uploaders:
            if u.email:
                send_email(u.email, "Daily KPI Upload", "Good morning. Please remember to upload your KPI data today.")

# Task 2: Overdue Check (Corrected for New Roles)
# Updated Overdue Check to handle Daily, Weekly, and Monthly
@scheduler.task('cron', id='overdue_job', hour=10, minute=0)
def job_overdue_check():
    with app.app_context():
        today = date.today()
        
        # 1. Calculate Target Dates
        # For Weekly: Find the Monday of the current week
        days_since_monday = today.weekday()
        current_monday = today - timedelta(days=days_since_monday)
        
        # For Monthly: Find the 1st of the current month
        first_of_month = today.replace(day=1)
        
        # 2. Get the Boss
        boss = User.query.filter_by(username='MrUpendra').first()
        
        # 3. Define Checks with specific Target Dates
        checks = [
            # --- DAILY CHECKS (Target: today) ---
            {'role': 'uploader_balance',     'model': DailyBalance,       'name': 'Daily Bank Balances',        'target': today},
            {'role': 'uploader_sales',       'model': SalesData,          'name': 'Sales KPIs',                 'target': today},
            {'role': 'uploader_scrap',       'model': ScrapData,          'name': 'Scrap Purchase KPIs',        'target': today},
            {'role': 'uploader_sponge',      'model': ProductionSponge,   'name': 'Sponge Iron Production',     'target': today},
            {'role': 'uploader_plant',       'model': ProductionMain,     'name': 'Billets/Rolling Production', 'target': today},
            {'role': 'uploader_plant',       'model': OperationalData,    'name': 'Power Outages',              'target': today},
            {'role': 'uploader_plant',       'model': GasPlantData,       'name': 'Gas Plant Data',             'target': today},

            # --- WEEKLY CHECKS (Target: current_monday) ---
            {'role': 'uploader_payables',    'model': AccountPayables,    'name': 'Account Payables',           'target': current_monday},
            {'role': 'uploader_receivables', 'model': AccountReceivables, 'name': 'Account Receivables',        'target': current_monday},

            # --- MONTHLY CHECKS (Target: first_of_month) ---
            {'role': 'uploader_interest',    'model': BankInterest,       'name': 'Bank Interest',              'target': first_of_month},
        ]

        # 4. Loop and Check
        for check in checks:
            target_date = check['target']
            
            # Look for entry on the specific target date
            data_exists = check['model'].query.filter_by(date=target_date).first()
            
            if not data_exists:
                uploader = User.query.filter_by(role=check['role']).first()
                if uploader:
                    print(f"MISSING DATA: {check['name']} (Expected Date: {target_date})")
                    
                    # Email Content
                    subject = f"URGENT: {check['name']} Overdue"
                    body = f"Hello {uploader.username},\n\nYou have not uploaded the {check['name']} for {target_date.strftime('%A, %d %B %Y')}. Please upload it immediately."
                    
                    # A. Notify Uploader
                    if uploader.email:
                        send_email(uploader.email, subject, body)
                    
                    # B. Notify Viewer (Boss)
                    if boss and boss.email:
                        boss_body = f"ALERT: {check['name']} Missing\n\nUser: {uploader.username}\nExpected Date: {target_date}"
                        send_email(boss.email, f"ALERT: {check['name']} Missing", boss_body)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)