import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime, timedelta
import sqlite3
import csv
import os
import sys
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

BG = '#118C4F'
BG_DARK = '#0D713F'
BG_LIGHT = '#EAF7F0'
WHITE = '#FFFFFF'
TEXT = '#153B2C'
MUTED = '#6D7D75'
BORDER = '#D9E5DF'
SUCCESS = '#10B981'
WARNING = '#F59E0B'
DANGER = '#EF4444'

APP_NAME = 'Harcama Bilgi Sistemi'
VERSION = '2.0 Advanced'
COMPANY_LINE = 'Kamacıoğlu Et Entegre (Veteriner Hekim Berk Can TAŞDEMİR)'


def database_path():
    if getattr(sys, 'frozen', False):
        data_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'HBS')
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, 'hbs_data.db')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hbs_data.db')


DB = database_path()


class HBSAdvancedApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f'{APP_NAME} • HBS {VERSION}')
        self.geometry('1400x850')
        self.minsize(1200, 750)
        self.configure(bg=BG_LIGHT)
        self.conn = sqlite3.connect(DB)
        self.sort_state = {'column': 'date', 'descending': True}
        self._ensure_db()
        self._style()
        self._build()
        self._load()

    def _ensure_db(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                kind TEXT NOT NULL,
                category TEXT DEFAULT 'Diğer',
                amount REAL NOT NULL,
                expense_date TEXT NOT NULL,
                payer TEXT,
                invoice TEXT,
                method TEXT,
                note TEXT
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                amount REAL NOT NULL,
                income_date TEXT NOT NULL,
                method TEXT,
                note TEXT
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL UNIQUE,
                limit REAL NOT NULL,
                month TEXT NOT NULL
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT DEFAULT '#118C4F'
            )
        ''')
        self.conn.commit()

    def _style(self):
        s = ttk.Style(self)
        s.theme_use('clam')
        s.configure('TFrame', background=BG_LIGHT)
        s.configure('TLabel', background=BG_LIGHT, foreground=TEXT, font=('Segoe UI', 10))
        s.configure('Treeview', background=WHITE, fieldbackground=WHITE, foreground=TEXT,
                    rowheight=34, font=('Segoe UI', 9))
        s.configure('Treeview.Heading', background=BG, foreground=WHITE,
                    font=('Segoe UI', 9, 'bold'), padding=(8, 8))
        s.map('Treeview', background=[('selected', BG)], foreground=[('selected', WHITE)])
        s.configure('Accent.TButton', background=BG, foreground=WHITE,
                    font=('Segoe UI', 9, 'bold'), padding=(14, 9), borderwidth=0)
        s.map('Accent.TButton', background=[('active', BG_DARK)])
        s.configure('Soft.TButton', background=WHITE, foreground=TEXT,
                    font=('Segoe UI', 9, 'bold'), padding=(12, 9), borderwidth=1)
        s.configure('TEntry', fieldbackground=WHITE, foreground=TEXT, padding=8)

    def _build(self):
        # Üst Başlık
        header = tk.Frame(self, bg=BG, height=110)
        header.pack(fill='x')
        tk.Label(header, text='HARCAMA BİLGİ SİSTEMİ', bg=BG, fg=WHITE,
                 font=('Segoe UI', 23, 'bold')).pack(anchor='w', padx=28, pady=(18, 1))
        tk.Label(header, text=f'HBS • İşletme Harcama Kayıt ve Takip Sistemi   |   {COMPANY_LINE}',
                 bg=BG, fg='#D8F5E5', font=('Segoe UI', 10)).pack(anchor='w', padx=30)
        tk.Label(header, text=f'Sürüm {VERSION}', bg=BG, fg='#BCE8CE',
                 font=('Segoe UI', 9, 'bold')).pack(anchor='e', padx=28, pady=(0, 10))

        # Ana Tab Paneli
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Dashboard
        self._build_dashboard_tab()
        
        # Tab 2: Harcama Yönetimi
        self._build_expense_tab()
        
        # Tab 3: Gelir Yönetimi
        self._build_income_tab()
        
        # Tab 4: Grafik ve İstatistikler
        self._build_analytics_tab()
        
        # Tab 5: Bütçe Yönetimi
        self._build_budget_tab()
        
        # Tab 6: Raporlama
        self._build_reports_tab()

    def _build_dashboard_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='📊 Dashboard')
        
        body = tk.Frame(frame, bg=BG_LIGHT)
        body.pack(fill='both', expand=True, padx=22, pady=18)
        
        # Kartlar
        cards = tk.Frame(body, bg=BG_LIGHT)
        cards.pack(fill='x', pady=(0, 14))
        self.card_total = self._card(cards, 'TOPLAM HARCAMA', '₺ 0,00', '#EF4444')
        self.card_income = self._card(cards, 'TOPLAM GELİR', '₺ 0,00', '#10B981')
        self.card_net = self._card(cards, 'NET KAR/ZARAR', '₺ 0,00', '#3B82F6')
        self.card_month = self._card(cards, 'BU AY HARCAMA', '₺ 0,00', '#F59E0B')

    def _build_expense_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='💸 Harcama Yönetimi')
        
        body = tk.Frame(frame, bg=BG_LIGHT)
        body.pack(fill='both', expand=True, padx=22, pady=18)
        
        # Form Panel
        panel = tk.Frame(body, bg=WHITE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        panel.pack(fill='x', pady=(0, 14))
        
        form = tk.Frame(panel, bg=WHITE)
        form.pack(fill='x', padx=16, pady=14)
        
        self.expense_vars = {k: tk.StringVar() for k in ['name', 'kind', 'category', 'amount', 'date', 'method', 'note']}
        self.expense_vars['date'].set(date.today().strftime('%d.%m.%Y'))
        
        fields = [
            ('Harcama Adı *', 'name', 0, 0),
            ('Harcama Türü *', 'kind', 0, 2),
            ('Kategori *', 'category', 0, 4),
            ('Maliyet (TL) *', 'amount', 1, 0),
            ('Tarih *', 'date', 1, 2),
            ('Ödeme Yöntemi', 'method', 1, 4),
            ('Açıklama', 'note', 2, 0),
        ]
        
        for label, key, row, col in fields:
            tk.Label(form, text=label, bg=WHITE, fg=MUTED,
                     font=('Segoe UI', 8, 'bold')).grid(
                         row=row * 2, column=col, sticky='w', padx=(0, 8), pady=(0, 4))
            width = 24 if key == 'note' else 20
            w = ttk.Entry(form, textvariable=self.expense_vars[key], width=width)
            w.grid(row=row * 2 + 1, column=col, sticky='ew', padx=(0, 14), pady=(0, 7))
        
        for c in [1, 3, 5]:
            form.columnconfigure(c, weight=1)
        
        # Butonlar
        btns = tk.Frame(panel, bg=WHITE)
        btns.pack(fill='x', padx=16, pady=(0, 14))
        ttk.Button(btns, text='＋ Harcama Kaydet', style='Accent.TButton', command=self.add_expense).pack(side='left')
        ttk.Button(btns, text='Formu Temizle', style='Soft.TButton', command=self.clear_expense_form).pack(side='left', padx=8)
        ttk.Button(btns, text='Excel Aktar', style='Soft.TButton', command=self.export_expenses_csv).pack(side='right')
        ttk.Button(btns, text='Seçili Sil', style='Soft.TButton', command=self.delete_expense).pack(side='right', padx=8)
        
        # Arama ve Tablo
        search = tk.Frame(body, bg=BG_LIGHT)
        search.pack(fill='x', pady=(0, 8))
        tk.Label(search, text='HARCAMALAR', bg=BG_LIGHT, fg=TEXT,
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        tk.Label(search, text='Ara:', bg=BG_LIGHT, fg=MUTED,
                 font=('Segoe UI', 9)).pack(side='right', padx=(10, 5))
        self.expense_q = tk.StringVar()
        ttk.Entry(search, textvariable=self.expense_q, width=28).pack(side='right')
        self.expense_q.trace_add('write', lambda *_: self._load_expenses())
        
        table_frame = tk.Frame(body, bg=WHITE, highlightthickness=1, highlightbackground=BORDER)
        table_frame.pack(fill='both', expand=True)
        
        cols = ('name', 'kind', 'category', 'amount', 'date', 'method', 'note')
        self.expense_headings = {
            'name': 'Harcama Adı',
            'kind': 'Türü',
            'category': 'Kategori',
            'amount': 'Maliyet (TL)',
            'date': 'Tarih',
            'method': 'Ödeme Yöntemi',
            'note': 'Açıklama'
        }
        widths = {'name': 180, 'kind': 120, 'category': 100, 'amount': 110, 'date': 90, 'method': 140, 'note': 250}
        
        self.expense_tree = ttk.Treeview(table_frame, columns=cols, show='headings', selectmode='extended')
        for c in cols:
            self.expense_tree.heading(c, text=self.expense_headings[c])
            self.expense_tree.column(c, width=widths[c], anchor='center' if c in ('amount', 'date') else 'w')
        
        vs = ttk.Scrollbar(table_frame, orient='vertical', command=self.expense_tree.yview)
        hs = ttk.Scrollbar(table_frame, orient='horizontal', command=self.expense_tree.xview)
        self.expense_tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.expense_tree.grid(row=0, column=0, sticky='nsew')
        vs.grid(row=0, column=1, sticky='ns')
        hs.grid(row=1, column=0, sticky='ew')
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.expense_tree.bind('<Double-1>', self.load_expense_to_form)

    def _build_income_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='💰 Gelir Yönetimi')
        
        body = tk.Frame(frame, bg=BG_LIGHT)
        body.pack(fill='both', expand=True, padx=22, pady=18)
        
        # Form Panel
        panel = tk.Frame(body, bg=WHITE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        panel.pack(fill='x', pady=(0, 14))
        
        form = tk.Frame(panel, bg=WHITE)
        form.pack(fill='x', padx=16, pady=14)
        
        self.income_vars = {k: tk.StringVar() for k in ['source', 'amount', 'date', 'method', 'note']}
        self.income_vars['date'].set(date.today().strftime('%d.%m.%Y'))
        
        fields = [
            ('Gelir Kaynağı *', 'source', 0, 0),
            ('Miktar (TL) *', 'amount', 0, 2),
            ('Tarih *', 'date', 0, 4),
            ('Ödeme Yöntemi', 'method', 1, 0),
            ('Açıklama', 'note', 1, 2),
        ]
        
        for label, key, row, col in fields:
            tk.Label(form, text=label, bg=WHITE, fg=MUTED,
                     font=('Segoe UI', 8, 'bold')).grid(
                         row=row * 2, column=col, sticky='w', padx=(0, 8), pady=(0, 4))
            width = 24 if key == 'note' else 20
            w = ttk.Entry(form, textvariable=self.income_vars[key], width=width)
            w.grid(row=row * 2 + 1, column=col, sticky='ew', padx=(0, 14), pady=(0, 7))
        
        for c in [1, 3, 5]:
            form.columnconfigure(c, weight=1)
        
        # Butonlar
        btns = tk.Frame(panel, bg=WHITE)
        btns.pack(fill='x', padx=16, pady=(0, 14))
        ttk.Button(btns, text='＋ Gelir Kaydet', style='Accent.TButton', command=self.add_income).pack(side='left')
        ttk.Button(btns, text='Formu Temizle', style='Soft.TButton', command=self.clear_income_form).pack(side='left', padx=8)
        ttk.Button(btns, text='Excel Aktar', style='Soft.TButton', command=self.export_income_csv).pack(side='right')
        ttk.Button(btns, text='Seçili Sil', style='Soft.TButton', command=self.delete_income).pack(side='right', padx=8)
        
        # Arama ve Tablo
        search = tk.Frame(body, bg=BG_LIGHT)
        search.pack(fill='x', pady=(0, 8))
        tk.Label(search, text='GELİRLER', bg=BG_LIGHT, fg=TEXT,
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        tk.Label(search, text='Ara:', bg=BG_LIGHT, fg=MUTED,
                 font=('Segoe UI', 9)).pack(side='right', padx=(10, 5))
        self.income_q = tk.StringVar()
        ttk.Entry(search, textvariable=self.income_q, width=28).pack(side='right')
        self.income_q.trace_add('write', lambda *_: self._load_income())
        
        table_frame = tk.Frame(body, bg=WHITE, highlightthickness=1, highlightbackground=BORDER)
        table_frame.pack(fill='both', expand=True)
        
        cols = ('source', 'amount', 'date', 'method', 'note')
        self.income_headings = {
            'source': 'Gelir Kaynağı',
            'amount': 'Miktar (TL)',
            'date': 'Tarih',
            'method': 'Ödeme Yöntemi',
            'note': 'Açıklama'
        }
        widths = {'source': 200, 'amount': 120, 'date': 100, 'method': 150, 'note': 300}
        
        self.income_tree = ttk.Treeview(table_frame, columns=cols, show='headings', selectmode='extended')
        for c in cols:
            self.income_tree.heading(c, text=self.income_headings[c])
            self.income_tree.column(c, width=widths[c], anchor='center' if c in ('amount', 'date') else 'w')
        
        vs = ttk.Scrollbar(table_frame, orient='vertical', command=self.income_tree.yview)
        hs = ttk.Scrollbar(table_frame, orient='horizontal', command=self.income_tree.xview)
        self.income_tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.income_tree.grid(row=0, column=0, sticky='nsew')
        vs.grid(row=0, column=1, sticky='ns')
        hs.grid(row=1, column=0, sticky='ew')
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

    def _build_analytics_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='📈 Grafik & İstatistikler')
        
        body = tk.Frame(frame, bg=BG_LIGHT)
        body.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Kontrol paneli
        control = tk.Frame(body, bg=WHITE, highlightthickness=1, highlightbackground=BORDER)
        control.pack(fill='x', pady=(0, 10))
        
        tk.Label(control, text='Dönem Seçin:', bg=WHITE, fg=TEXT, font=('Segoe UI', 9, 'bold')).pack(side='left', padx=10, pady=10)
        
        self.chart_period = tk.StringVar(value='month')
        periods = [('Bu Ay', 'month'), ('Son 3 Ay', '3month'), ('Son 6 Ay', '6month'), ('Tüm Veriler', 'all')]
        for text, value in periods:
            ttk.Radiobutton(control, text=text, variable=self.chart_period, value=value,
                           command=self._refresh_analytics).pack(side='left', padx=5)
        
        ttk.Button(control, text='Grafikleri Yenile', command=self._refresh_analytics).pack(side='right', padx=10, pady=10)
        
        # Grafik alanları
        self.analytics_frame = tk.Frame(body, bg=BG_LIGHT)
        self.analytics_frame.pack(fill='both', expand=True)

    def _build_budget_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='🎯 Bütçe Yönetimi')
        
        body = tk.Frame(frame, bg=BG_LIGHT)
        body.pack(fill='both', expand=True, padx=22, pady=18)
        
        # Bütçe Ekleme Formu
        panel = tk.Frame(body, bg=WHITE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        panel.pack(fill='x', pady=(0, 14))
        
        form = tk.Frame(panel, bg=WHITE)
        form.pack(fill='x', padx=16, pady=14)
        
        self.budget_vars = {k: tk.StringVar() for k in ['category', 'limit', 'month']}
        self.budget_vars['month'].set(datetime.now().strftime('%Y-%m'))
        
        tk.Label(form, text='Kategori *', bg=WHITE, fg=MUTED,
                 font=('Segoe UI', 8, 'bold')).grid(row=0, column=0, sticky='w', padx=(0, 8), pady=(0, 4))
        ttk.Entry(form, textvariable=self.budget_vars['category'], width=20).grid(row=1, column=0, sticky='ew', padx=(0, 14), pady=(0, 7))
        
        tk.Label(form, text='Limit (TL) *', bg=WHITE, fg=MUTED,
                 font=('Segoe UI', 8, 'bold')).grid(row=0, column=1, sticky='w', padx=(0, 8), pady=(0, 4))
        ttk.Entry(form, textvariable=self.budget_vars['limit'], width=20).grid(row=1, column=1, sticky='ew', padx=(0, 14), pady=(0, 7))
        
        tk.Label(form, text='Ay (YYYY-MM) *', bg=WHITE, fg=MUTED,
                 font=('Segoe UI', 8, 'bold')).grid(row=0, column=2, sticky='w', padx=(0, 8), pady=(0, 4))
        ttk.Entry(form, textvariable=self.budget_vars['month'], width=20).grid(row=1, column=2, sticky='ew', padx=(0, 14), pady=(0, 7))
        
        form.columnconfigure(1, weight=1)
        
        btns = tk.Frame(panel, bg=WHITE)
        btns.pack(fill='x', padx=16, pady=(0, 14))
        ttk.Button(btns, text='＋ Bütçe Ekle', style='Accent.TButton', command=self.add_budget).pack(side='left')
        ttk.Button(btns, text='Seçili Sil', style='Soft.TButton', command=self.delete_budget).pack(side='left', padx=8)
        
        # Bütçe Tablosu
        table_frame = tk.Frame(body, bg=WHITE, highlightthickness=1, highlightbackground=BORDER)
        table_frame.pack(fill='both', expand=True)
        
        cols = ('category', 'limit', 'spent', 'remaining', 'month', 'status')
        self.budget_headings = {
            'category': 'Kategori',
            'limit': 'Limit (TL)',
            'spent': 'Harcanan (TL)',
            'remaining': 'Kalan (TL)',
            'month': 'Ay',
            'status': 'Durum'
        }
        widths = {'category': 150, 'limit': 120, 'spent': 120, 'remaining': 120, 'month': 100, 'status': 100}
        
        self.budget_tree = ttk.Treeview(table_frame, columns=cols, show='headings', selectmode='extended')
        for c in cols:
            self.budget_tree.heading(c, text=self.budget_headings[c])
            self.budget_tree.column(c, width=widths[c], anchor='center')
        
        vs = ttk.Scrollbar(table_frame, orient='vertical', command=self.budget_tree.yview)
        self.budget_tree.configure(yscrollcommand=vs.set)
        self.budget_tree.grid(row=0, column=0, sticky='nsew')
        vs.grid(row=0, column=1, sticky='ns')
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        self._load_budgets()

    def _build_reports_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='📋 Raporlama')
        
        body = tk.Frame(frame, bg=BG_LIGHT)
        body.pack(fill='both', expand=True, padx=22, pady=18)
        
        # Rapor Filtresi
        panel = tk.Frame(body, bg=WHITE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        panel.pack(fill='x', pady=(0, 14))
        
        form = tk.Frame(panel, bg=WHITE)
        form.pack(fill='x', padx=16, pady=14)
        
        self.report_vars = {k: tk.StringVar() for k in ['start_date', 'end_date', 'category', 'report_type']}
        self.report_vars['start_date'].set((date.today() - timedelta(days=30)).strftime('%d.%m.%Y'))
        self.report_vars['end_date'].set(date.today().strftime('%d.%m.%Y'))
        self.report_vars['report_type'].set('summary')
        
        tk.Label(form, text='Başlangıç Tarihi', bg=WHITE, fg=MUTED, font=('Segoe UI', 8, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 4))
        ttk.Entry(form, textvariable=self.report_vars['start_date'], width=18).grid(row=1, column=0, sticky='ew', padx=(0, 14), pady=(0, 7))
        
        tk.Label(form, text='Bitiş Tarihi', bg=WHITE, fg=MUTED, font=('Segoe UI', 8, 'bold')).grid(row=0, column=1, sticky='w', pady=(0, 4))
        ttk.Entry(form, textvariable=self.report_vars['end_date'], width=18).grid(row=1, column=1, sticky='ew', padx=(0, 14), pady=(0, 7))
        
        tk.Label(form, text='Kategori (Boş=Hepsi)', bg=WHITE, fg=MUTED, font=('Segoe UI', 8, 'bold')).grid(row=0, column=2, sticky='w', pady=(0, 4))
        ttk.Entry(form, textvariable=self.report_vars['category'], width=18).grid(row=1, column=2, sticky='ew', padx=(0, 14), pady=(0, 7))
        
        form.columnconfigure(1, weight=1)
        
        btns = tk.Frame(panel, bg=WHITE)
        btns.pack(fill='x', padx=16, pady=(0, 14))
        ttk.Button(btns, text='Rapor Oluştur', style='Accent.TButton', command=self.generate_report).pack(side='left')
        ttk.Button(btns, text='Raporu PDF Aktar', style='Soft.TButton', command=self.export_report_pdf).pack(side='left', padx=8)
        
        # Rapor Görüntü Alanı
        self.report_frame = tk.Frame(body, bg=WHITE, highlightthickness=1, highlightbackground=BORDER)
        self.report_frame.pack(fill='both', expand=True)

    def _card(self, parent, title, value, color='#118C4F'):
        f = tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground=BORDER)
        f.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Renk çubuğu
        tk.Frame(f, bg=color, height=4).pack(fill='x')
        
        tk.Label(f, text=title, bg=WHITE, fg=MUTED, font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=15, pady=(12, 2))
        l = tk.Label(f, text=value, bg=WHITE, fg=TEXT, font=('Segoe UI', 18, 'bold'))
        l.pack(anchor='w', padx=15, pady=(0, 12))
        return l

    # ===== HARCAMA FONKSİYONLARI =====
    def add_expense(self):
        name = self.expense_vars['name'].get().strip()
        kind = self.expense_vars['kind'].get().strip()
        category = self.expense_vars['category'].get().strip()
        amt = self.expense_vars['amount'].get().strip()
        
        if not name or not kind or not category or not amt:
            messagebox.showwarning('Eksik Bilgi', 'Harcama adı, türü, kategori ve maliyet zorunludur.')
            return
        
        try:
            amount = self._parse_amount(amt)
        except ValueError:
            messagebox.showerror('Geçersiz Maliyet', 'Sayısal değer girin.')
            return
        
        if amount < 0:
            messagebox.showerror('Geçersiz Maliyet', 'Maliyet negatif olamaz.')
            return
        
        try:
            dt = datetime.strptime(self.expense_vars['date'].get().strip(), '%d.%m.%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Geçersiz Tarih', 'Tarih biçimi GG.AA.YYYY olmalıdır.')
            return
        
        self.conn.execute(
            'INSERT INTO expenses(name, kind, category, amount, expense_date, method, note) VALUES(?,?,?,?,?,?,?)',
            (name, kind, category, amount, dt, self.expense_vars['method'].get().strip(), self.expense_vars['note'].get().strip())
        )
        self.conn.commit()
        self.clear_expense_form()
        self._load_expenses()
        self._update_dashboard()
        messagebox.showinfo('Başarılı', 'Harcama kaydedildi!')

    def clear_expense_form(self):
        for k in ['name', 'kind', 'category', 'amount', 'method', 'note']:
            self.expense_vars[k].set('')
        self.expense_vars['date'].set(date.today().strftime('%d.%m.%Y'))

    def delete_expense(self):
        sel = self.expense_tree.selection()
        if not sel:
            messagebox.showwarning('Seçim Yok', 'Silmek için bir kayıt seçin.')
            return
        
        if not messagebox.askyesno('Onay', f'{len(sel)} kaydı silmek istiyor musunuz?'):
            return
        
        self.conn.executemany('DELETE FROM expenses WHERE id=?', [(i,) for i in sel])
        self.conn.commit()
        self._load_expenses()
        self._update_dashboard()

    def load_expense_to_form(self, event):
        sel = self.expense_tree.selection()
        if not sel:
            return
        row_id = sel[0]
        row = self.conn.execute(
            'SELECT name, kind, category, amount, expense_date, method, note FROM expenses WHERE id=?', (row_id,)
        ).fetchone()
        if not row:
            return
        self.expense_vars['name'].set(row[0])
        self.expense_vars['kind'].set(row[1])
        self.expense_vars['category'].set(row[2])
        self.expense_vars['amount'].set(str(row[3]).replace('.', ','))
        self.expense_vars['date'].set(datetime.strptime(row[4], '%Y-%m-%d').strftime('%d.%m.%Y'))
        self.expense_vars['method'].set(row[5] or '')
        self.expense_vars['note'].set(row[6] or '')

    def export_expenses_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV Dosyası', '*.csv')],
            initialfile=f'Harcamalar_{date.today().strftime("%d.%m.%Y")}.csv'
        )
        if not path:
            return
        
        rows = self.conn.execute(
            'SELECT name, kind, category, amount, expense_date, method, note FROM expenses ORDER BY expense_date DESC, id DESC'
        ).fetchall()
        
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(['Harcama Adı', 'Türü', 'Kategori', 'Maliyet (TL)', 'Tarih', 'Ödeme Yöntemi', 'Açıklama'])
            for r in rows:
                w.writerow([r[0], r[1], r[2], r[3], r[4], r[5] or '', r[6] or ''])
        
        messagebox.showinfo('Başarılı', f'Rapor kaydedildi:\n{path}')

    def _load_expenses(self):
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        q = self.expense_q.get().strip().lower()
        rows = self.conn.execute(
            'SELECT id, name, kind, category, amount, expense_date, method, note FROM expenses'
        ).fetchall()
        
        for row in rows:
            text = ' '.join('' if v is None else str(v) for v in row).lower()
            if q and q not in text:
                continue
            self.expense_tree.insert(
                '', 'end', iid=str(row[0]),
                values=(row[1], row[2], row[3], self._money(row[4]),
                        datetime.strptime(row[5], '%Y-%m-%d').strftime('%d.%m.%Y'),
                        row[6] or '', row[7] or '')
            )

    # ===== GELİR FONKSİYONLARI =====
    def add_income(self):
        source = self.income_vars['source'].get().strip()
        amt = self.income_vars['amount'].get().strip()
        
        if not source or not amt:
            messagebox.showwarning('Eksik Bilgi', 'Gelir kaynağı ve miktar zorunludur.')
            return
        
        try:
            amount = self._parse_amount(amt)
        except ValueError:
            messagebox.showerror('Geçersiz Miktar', 'Sayısal değer girin.')
            return
        
        if amount < 0:
            messagebox.showerror('Geçersiz Miktar', 'Miktar negatif olamaz.')
            return
        
        try:
            dt = datetime.strptime(self.income_vars['date'].get().strip(), '%d.%m.%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Geçersiz Tarih', 'Tarih biçimi GG.AA.YYYY olmalıdır.')
            return
        
        self.conn.execute(
            'INSERT INTO income(source, amount, income_date, method, note) VALUES(?,?,?,?,?)',
            (source, amount, dt, self.income_vars['method'].get().strip(), self.income_vars['note'].get().strip())
        )
        self.conn.commit()
        self.clear_income_form()
        self._load_income()
        self._update_dashboard()
        messagebox.showinfo('Başarılı', 'Gelir kaydedildi!')

    def clear_income_form(self):
        for k in ['source', 'amount', 'method', 'note']:
            self.income_vars[k].set('')
        self.income_vars['date'].set(date.today().strftime('%d.%m.%Y'))

    def delete_income(self):
        sel = self.income_tree.selection()
        if not sel:
            messagebox.showwarning('Seçim Yok', 'Silmek için bir kayıt seçin.')
            return
        
        if not messagebox.askyesno('Onay', f'{len(sel)} kaydı silmek istiyor musunuz?'):
            return
        
        self.conn.executemany('DELETE FROM income WHERE id=?', [(i,) for i in sel])
        self.conn.commit()
        self._load_income()
        self._update_dashboard()

    def export_income_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV Dosyası', '*.csv')],
            initialfile=f'Gelirler_{date.today().strftime("%d.%m.%Y")}.csv'
        )
        if not path:
            return
        
        rows = self.conn.execute(
            'SELECT source, amount, income_date, method, note FROM income ORDER BY income_date DESC, id DESC'
        ).fetchall()
        
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(['Gelir Kaynağı', 'Miktar (TL)', 'Tarih', 'Ödeme Yöntemi', 'Açıklama'])
            for r in rows:
                w.writerow([r[0], r[1], r[2], r[3] or '', r[4] or ''])
        
        messagebox.showinfo('Başarılı', f'Rapor kaydedildi:\n{path}')

    def _load_income(self):
        for item in self.income_tree.get_children():
            self.income_tree.delete(item)
        
        q = self.income_q.get().strip().lower()
        rows = self.conn.execute(
            'SELECT id, source, amount, income_date, method, note FROM income'
        ).fetchall()
        
        for row in rows:
            text = ' '.join('' if v is None else str(v) for v in row).lower()
            if q and q not in text:
                continue
            self.income_tree.insert(
                '', 'end', iid=str(row[0]),
                values=(row[1], self._money(row[2]),
                        datetime.strptime(row[3], '%Y-%m-%d').strftime('%d.%m.%Y'),
                        row[4] or '', row[5] or '')
            )

    # ===== BÜTÇE FONKSİYONLARI =====
    def add_budget(self):
        category = self.budget_vars['category'].get().strip()
        limit = self.budget_vars['limit'].get().strip()
        month = self.budget_vars['month'].get().strip()
        
        if not category or not limit or not month:
            messagebox.showwarning('Eksik Bilgi', 'Tüm alanlar zorunludur.')
            return
        
        try:
            limit_amount = self._parse_amount(limit)
        except ValueError:
            messagebox.showerror('Geçersiz Limit', 'Sayısal değer girin.')
            return
        
        try:
            datetime.strptime(month, '%Y-%m')
        except ValueError:
            messagebox.showerror('Geçersiz Ay', 'Ay biçimi YYYY-AA olmalıdır.')
            return
        
        self.conn.execute(
            'INSERT OR REPLACE INTO budgets(category, limit, month) VALUES(?,?,?)',
            (category, limit_amount, month)
        )
        self.conn.commit()
        self.budget_vars['category'].set('')
        self.budget_vars['limit'].set('')
        self._load_budgets()
        messagebox.showinfo('Başarılı', 'Bütçe kaydedildi!')

    def delete_budget(self):
        sel = self.budget_tree.selection()
        if not sel:
            messagebox.showwarning('Seçim Yok', 'Silmek için bir bütçe seçin.')
            return
        
        for iid in sel:
            values = self.budget_tree.item(iid)['values']
            category = values[0]
            month = values[4]
            self.conn.execute('DELETE FROM budgets WHERE category=? AND month=?', (category, month))
        
        self.conn.commit()
        self._load_budgets()

    def _load_budgets(self):
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)
        
        budgets = self.conn.execute('SELECT category, limit, month FROM budgets ORDER BY month DESC').fetchall()
        
        for category, limit, month in budgets:
            spent = self.conn.execute(
                'SELECT SUM(amount) FROM expenses WHERE category=? AND expense_date LIKE ?',
                (category, f'{month}%')
            ).fetchone()[0] or 0
            
            remaining = limit - spent
            status = '✓ OK' if remaining >= 0 else '✗ AŞTI'
            status_color = SUCCESS if remaining >= 0 else DANGER
            
            self.budget_tree.insert('', 'end', values=(
                category, self._money(limit), self._money(spent),
                self._money(remaining), month, status
            ))

    # ===== DASHBOARD =====
    def _update_dashboard(self):
        now = datetime.now()
        
        total_expense = self.conn.execute('SELECT SUM(amount) FROM expenses').fetchone()[0] or 0
        total_income = self.conn.execute('SELECT SUM(amount) FROM income').fetchone()[0] or 0
        
        month_expense = self.conn.execute(
            'SELECT SUM(amount) FROM expenses WHERE expense_date LIKE ?',
            (f'{now.year:04d}-{now.month:02d}%',)
        ).fetchone()[0] or 0
        
        net = total_income - total_expense
        
        self.card_total.config(text=self._money(total_expense))
        self.card_income.config(text=self._money(total_income))
        self.card_net.config(text=self._money(net))
        self.card_month.config(text=self._money(month_expense))

    # ===== GRAFIK VE İSTATİSTİKLER =====
    def _refresh_analytics(self):
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()
        
        period = self.chart_period.get()
        start_date = self._get_period_start(period)
        
        # Grafikleri oluştur
        self._draw_monthly_chart(start_date)
        self._draw_category_chart(start_date)
        self._draw_payment_chart(start_date)
        self._draw_trend_chart(start_date)

    def _get_period_start(self, period):
        now = datetime.now()
        if period == 'month':
            return now.replace(day=1)
        elif period == '3month':
            return now - timedelta(days=90)
        elif period == '6month':
            return now - timedelta(days=180)
        else:
            return datetime(2020, 1, 1)

    def _draw_monthly_chart(self, start_date):
        data = self.conn.execute(
            'SELECT expense_date, SUM(amount) FROM expenses WHERE expense_date >= ? GROUP BY expense_date ORDER BY expense_date',
            (start_date.strftime('%Y-%m-%d'),)
        ).fetchall()
        
        frame = tk.Frame(self.analytics_frame, bg=BG_LIGHT)
        frame.pack(side='left', fill='both', expand=True, padx=5)
        
        fig = Figure(figsize=(5, 4), dpi=80, facecolor=BG_LIGHT)
        ax = fig.add_subplot(111)
        
        dates = [datetime.strptime(d[0], '%Y-%m-%d') for d in data]
        amounts = [d[1] for d in data]
        
        ax.plot(dates, amounts, marker='o', color=BG, linewidth=2, markersize=6)
        ax.fill_between(dates, amounts, alpha=0.3, color=BG)
        ax.set_title('Günlük Harcama Trendi', fontsize=12, fontweight='bold', color=TEXT)
        ax.set_xlabel('Tarih', fontsize=10, color=TEXT)
        ax.set_ylabel('Miktar (TL)', fontsize=10, color=TEXT)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        fig.autofmt_xdate()
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _draw_category_chart(self, start_date):
        data = self.conn.execute(
            'SELECT category, SUM(amount) FROM expenses WHERE expense_date >= ? GROUP BY category ORDER BY SUM(amount) DESC',
            (start_date.strftime('%Y-%m-%d'),)
        ).fetchall()
        
        frame = tk.Frame(self.analytics_frame, bg=BG_LIGHT)
        frame.pack(side='left', fill='both', expand=True, padx=5)
        
        fig = Figure(figsize=(5, 4), dpi=80, facecolor=BG_LIGHT)
        ax = fig.add_subplot(111)
        
        if data:
            categories = [d[0] for d in data]
            amounts = [d[1] for d in data]
            
            colors = ['#118C4F', '#10B981', '#34D399', '#6EE7B7', '#A7F3D0']
            ax.pie(amounts, labels=categories, autopct='%1.1f%%', colors=colors, startangle=90)
            ax.set_title('Kategoriye Göre Dağılım', fontsize=12, fontweight='bold', color=TEXT)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _draw_payment_chart(self, start_date):
        data = self.conn.execute(
            'SELECT method, SUM(amount) FROM expenses WHERE expense_date >= ? AND method IS NOT NULL GROUP BY method ORDER BY SUM(amount) DESC',
            (start_date.strftime('%Y-%m-%d'),)
        ).fetchall()
        
        frame = tk.Frame(self.analytics_frame, bg=BG_LIGHT)
        frame.pack(side='left', fill='both', expand=True, padx=5)
        
        fig = Figure(figsize=(5, 4), dpi=80, facecolor=BG_LIGHT)
        ax = fig.add_subplot(111)
        
        if data:
            methods = [d[0] for d in data]
            amounts = [d[1] for d in data]
            
            ax.barh(methods, amounts, color=BG)
            ax.set_title('Ödeme Yöntemine Göre', fontsize=12, fontweight='bold', color=TEXT)
            ax.set_xlabel('Miktar (TL)', fontsize=10, color=TEXT)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _draw_trend_chart(self, start_date):
        # Aylık karşılaştırma
        data = self.conn.execute(
            'SELECT strftime("%Y-%m", expense_date), SUM(amount) FROM expenses WHERE expense_date >= ? GROUP BY strftime("%Y-%m", expense_date) ORDER BY expense_date',
            (start_date.strftime('%Y-%m-%d'),)
        ).fetchall()
        
        frame = tk.Frame(self.analytics_frame, bg=BG_LIGHT)
        frame.pack(side='left', fill='both', expand=True, padx=5)
        
        fig = Figure(figsize=(5, 4), dpi=80, facecolor=BG_LIGHT)
        ax = fig.add_subplot(111)
        
        if data:
            months = [d[0] for d in data]
            amounts = [d[1] for d in data]
            
            ax.bar(months, amounts, color=BG, alpha=0.8, edgecolor=BG_DARK)
            ax.set_title('Aylık Harcama Toplamı', fontsize=12, fontweight='bold', color=TEXT)
            ax.set_ylabel('Miktar (TL)', fontsize=10, color=TEXT)
            ax.tick_params(axis='x', rotation=45)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    # ===== RAPORLAMA =====
    def generate_report(self):
        try:
            start = datetime.strptime(self.report_vars['start_date'].get(), '%d.%m.%Y').strftime('%Y-%m-%d')
            end = datetime.strptime(self.report_vars['end_date'].get(), '%d.%m.%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Geçersiz Tarih', 'Tarih biçimi GG.AA.YYYY olmalıdır.')
            return
        
        category_filter = self.report_vars['category'].get().strip()
        
        query = 'SELECT category, SUM(amount) as total FROM expenses WHERE expense_date BETWEEN ? AND ?'
        params = [start, end]
        
        if category_filter:
            query += ' AND category = ?'
            params.append(category_filter)
        
        query += ' GROUP BY category ORDER BY total DESC'
        
        data = self.conn.execute(query, params).fetchall()
        
        # Raporu göster
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        txt = tk.Text(self.report_frame, bg=WHITE, fg=TEXT, font=('Courier', 10), wrap='word')
        txt.pack(fill='both', expand=True, padx=10, pady=10)
        
        report_text = f"""
╔══════════════════════════════════════════════════════════════════╗
║           HARCAMA RAPORu ({start} - {end})            ║
╚══════════════════════════════════════════════════════════════════╝

ÖZET:
"""
        
        total = sum(d[1] for d in data)
        report_text += f"Toplam Harcama: {self._money(total)}\n"
        report_text += f"Kayıt Sayısı: {len(data)}\n"
        report_text += f"Ortalama: {self._money(total / len(data) if data else 0)}\n\n"
        
        report_text += "KATEGORİ DETAYLARI:\n"
        report_text += "─" * 64 + "\n"
        report_text += f"{'Kategori':<30} {'Tutar (TL)':<20} {'Yüzde':<14}\n"
        report_text += "─" * 64 + "\n"
        
        for category, amount in data:
            percentage = (amount / total * 100) if total > 0 else 0
            report_text += f"{category:<30} {self._money(amount):<20} {percentage:>6.1f}%\n"
        
        report_text += "─" * 64 + "\n"
        report_text += f"{'TOPLAM':<30} {self._money(total):<20} {'100.0%':>6}\n"
        
        txt.insert('end', report_text)
        txt.config(state='disabled')

    def export_report_pdf(self):
        messagebox.showinfo('Bilgi', 'PDF export özelliği yakında eklenecektir.')

    # ===== YARDIMCI FONKSİYONLAR =====
    @staticmethod
    def _parse_amount(text):
        t = text.strip().replace('₺', '').replace(' ', '')
        if ',' in t and '.' in t:
            if t.rfind(',') > t.rfind('.'):
                t = t.replace('.', '').replace(',', '.')
            else:
                t = t.replace(',', '')
        elif ',' in t:
            t = t.replace(',', '.')
        return float(t)

    @staticmethod
    def _money(value):
        return f'₺ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    def _load(self):
        self._load_expenses()
        self._load_income()
        self._update_dashboard()

    def on_close(self):
        try:
            self.conn.commit()
            self.conn.close()
        finally:
            self.destroy()


if __name__ == '__main__':
    app = HBSAdvancedApp()
    app.protocol('WM_DELETE_WINDOW', app.on_close)
    app.mainloop()
