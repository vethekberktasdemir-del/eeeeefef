import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime
import sqlite3
import csv
import os
import sys

BG = '#118C4F'
BG_DARK = '#0D713F'
BG_LIGHT = '#EAF7F0'
WHITE = '#FFFFFF'
TEXT = '#153B2C'
MUTED = '#6D7D75'
BORDER = '#D9E5DF'

APP_NAME = 'Harcama Bilgi Sistemi'
VERSION = '1.3'
COMPANY_LINE = 'Kamacıoğlu Et Entegre (Veteriner Hekim Berk Can TAŞDEMİR)'


def database_path():
    if getattr(sys, 'frozen', False):
        data_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'HBS')
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, 'hbs_data.db')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hbs_data.db')


DB = database_path()


class HBSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f'{APP_NAME} • HBS {VERSION}')
        self.geometry('1220x760')
        self.minsize(1050, 680)
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
                amount REAL NOT NULL,
                expense_date TEXT NOT NULL,
                payer TEXT,
                invoice TEXT,
                method TEXT,
                note TEXT
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
        header = tk.Frame(self, bg=BG, height=110)
        header.pack(fill='x')
        tk.Label(header, text='HARCAMA BİLGİ SİSTEMİ', bg=BG, fg=WHITE,
                 font=('Segoe UI', 23, 'bold')).pack(anchor='w', padx=28, pady=(18, 1))
        tk.Label(header, text=f'HBS • İşletme Harcama Kayıt ve Takip Sistemi   |   {COMPANY_LINE}',
                 bg=BG, fg='#D8F5E5', font=('Segoe UI', 10)).pack(anchor='w', padx=30)
        tk.Label(header, text=f'Sürüm {VERSION}', bg=BG, fg='#BCE8CE',
                 font=('Segoe UI', 9, 'bold')).pack(anchor='e', padx=28, pady=(0, 10))

        body = tk.Frame(self, bg=BG_LIGHT)
        body.pack(fill='both', expand=True, padx=22, pady=18)

        cards = tk.Frame(body, bg=BG_LIGHT)
        cards.pack(fill='x', pady=(0, 14))
        self.card_total = self._card(cards, 'TOPLAM HARCAMA', '₺ 0,00')
        self.card_month = self._card(cards, 'BU AY', '₺ 0,00')
        self.card_count = self._card(cards, 'KAYIT SAYISI', '0')
        self.card_avg = self._card(cards, 'ORTALAMA HARCAMA', '₺ 0,00')

        panel = tk.Frame(body, bg=WHITE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        panel.pack(fill='x', pady=(0, 14))

        form = tk.Frame(panel, bg=WHITE)
        form.pack(fill='x', padx=16, pady=14)

        self.vars = {k: tk.StringVar() for k in ['name', 'kind', 'amount', 'date', 'method', 'note']}
        self.vars['date'].set(date.today().strftime('%d.%m.%Y'))

        fields = [
            ('Harcama Adı *', 'name', 0, 0),
            ('Harcama Türü *', 'kind', 0, 2),
            ('Maliyet (TL) *', 'amount', 0, 4),
            ('Tarih *', 'date', 0, 6),
            ('Ödeme Yöntemi', 'method', 1, 0),
            ('Açıklama', 'note', 1, 2),
        ]
        for label, key, row, col in fields:
            tk.Label(form, text=label, bg=WHITE, fg=MUTED,
                     font=('Segoe UI', 8, 'bold')).grid(
                         row=row * 2, column=col, sticky='w', padx=(0, 8), pady=(0, 4))
            width = 24 if key == 'note' else 20
            w = ttk.Entry(form, textvariable=self.vars[key], width=width)
            w.grid(row=row * 2 + 1, column=col, sticky='ew', padx=(0, 14), pady=(0, 7))
        for c in [1, 3, 5, 7]:
            form.columnconfigure(c, weight=1)

        btns = tk.Frame(panel, bg=WHITE)
        btns.pack(fill='x', padx=16, pady=(0, 14))
        ttk.Button(btns, text='＋ Harcama Kaydet', style='Accent.TButton', command=self.add).pack(side='left')
        ttk.Button(btns, text='Formu Temizle', style='Soft.TButton', command=self.clear_form).pack(side='left', padx=8)
        ttk.Button(btns, text='Excel / CSV Aktar', style='Soft.TButton', command=self.export_csv).pack(side='right')
        ttk.Button(btns, text='Seçili Kaydı Sil', style='Soft.TButton', command=self.delete_selected).pack(side='right', padx=8)

        search = tk.Frame(body, bg=BG_LIGHT)
        search.pack(fill='x', pady=(0, 8))
        tk.Label(search, text='HARCAMALAR', bg=BG_LIGHT, fg=TEXT,
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        tk.Label(search, text='Ara:', bg=BG_LIGHT, fg=MUTED,
                 font=('Segoe UI', 9)).pack(side='right', padx=(10, 5))
        self.q = tk.StringVar()
        ttk.Entry(search, textvariable=self.q, width=28).pack(side='right')
        self.q.trace_add('write', lambda *_: self._load())

        tk.Label(search, text='• Sıralamak için sütun başlığına tıklayın',
                 bg=BG_LIGHT, fg=MUTED, font=('Segoe UI', 8)).pack(side='left', padx=12)

        table_frame = tk.Frame(body, bg=WHITE, highlightthickness=1, highlightbackground=BORDER)
        table_frame.pack(fill='both', expand=True)

        cols = ('name', 'kind', 'amount', 'date', 'method', 'note')
        self.headings = {
            'name': 'Harcama Adı',
            'kind': 'Harcama Türü',
            'amount': 'Maliyet (TL)',
            'date': 'Tarih',
            'method': 'Ödeme Yöntemi',
            'note': 'Açıklama'
        }
        widths = {'name': 230, 'kind': 150, 'amount': 125, 'date': 100, 'method': 160, 'note': 350}

        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings', selectmode='extended')
        for c in cols:
            self.tree.heading(c, text=self.headings[c], command=lambda col=c: self._sort_by(col))
            self.tree.column(c, width=widths[c], anchor='center' if c in ('amount', 'date') else 'w')

        vs = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        hs = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vs.grid(row=0, column=1, sticky='ns')
        hs.grid(row=1, column=0, sticky='ew')
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.tree.bind('<Double-1>', self.load_selected_to_form)

        self._refresh_heading_indicators()

    def _card(self, parent, title, value):
        f = tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground=BORDER)
        f.pack(side='left', fill='x', expand=True, padx=(0, 10))
        tk.Label(f, text=title, bg=WHITE, fg=MUTED,
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=15, pady=(12, 2))
        l = tk.Label(f, text=value, bg=WHITE, fg=TEXT,
                     font=('Segoe UI', 18, 'bold'))
        l.pack(anchor='w', padx=15, pady=(0, 12))
        return l

    def clear_form(self):
        for k in ['name', 'kind', 'amount', 'method', 'note']:
            self.vars[k].set('')
        self.vars['date'].set(date.today().strftime('%d.%m.%Y'))

    def add(self):
        name = self.vars['name'].get().strip()
        kind = self.vars['kind'].get().strip()
        amt = self.vars['amount'].get().strip()
        if not name or not kind or not amt:
            messagebox.showwarning('Eksik Bilgi', 'Harcama adı, harcama türü ve maliyet alanları zorunludur.')
            return

        try:
            amount = self._parse_amount(amt)
        except ValueError:
            messagebox.showerror('Geçersiz Maliyet', 'Maliyet alanına sayısal bir değer girin.')
            return
        if amount < 0:
            messagebox.showerror('Geçersiz Maliyet', 'Maliyet negatif olamaz.')
            return

        try:
            dt = datetime.strptime(self.vars['date'].get().strip(), '%d.%m.%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Geçersiz Tarih', 'Tarih biçimi GG.AA.YYYY olmalıdır.')
            return

        self.conn.execute(
            'INSERT INTO expenses(name, kind, amount, expense_date, method, note) VALUES(?,?,?,?,?,?)',
            (name, kind, amount, dt, self.vars['method'].get().strip(), self.vars['note'].get().strip())
        )
        self.conn.commit()
        self.clear_form()
        self._load()

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
        for item in self.tree.get_children():
            self.tree.delete(item)

        q = self.q.get().strip().lower()
        rows = self.conn.execute(
            'SELECT id, name, kind, amount, expense_date, method, note FROM expenses'
        ).fetchall()

        sort_col = self.sort_state['column']
        descending = self.sort_state['descending']
        key_index = {'name': 1, 'kind': 2, 'amount': 3, 'date': 4, 'method': 5, 'note': 6}[sort_col]
        if sort_col == 'date':
            rows.sort(key=lambda r: r[4] or '', reverse=descending)
        elif sort_col == 'amount':
            rows.sort(key=lambda r: float(r[3] or 0), reverse=descending)
        else:
            rows.sort(key=lambda r: (r[key_index] or '').casefold(), reverse=descending)

        shown = []
        for row in rows:
            text = ' '.join('' if v is None else str(v) for v in row).lower()
            if q and q not in text:
                continue
            shown.append(row)
            self.tree.insert(
                '', 'end', iid=str(row[0]),
                values=(row[1], row[2], self._money(row[3]),
                        datetime.strptime(row[4], '%Y-%m-%d').strftime('%d.%m.%Y'),
                        row[5] or '', row[6] or '')
            )
        self._refresh_cards(shown)
        self._refresh_heading_indicators()

    def _refresh_cards(self, rows):
        total = sum(float(r[3]) for r in rows)
        now = datetime.now()
        month = now.month
        year = now.year
        m = sum(float(r[3]) for r in rows if r[4].startswith(f'{year:04d}-{month:02d}-'))
        cnt = len(rows)
        avg = total / cnt if cnt else 0
        self.card_total.config(text=self._money(total))
        self.card_month.config(text=self._money(m))
        self.card_count.config(text=str(cnt))
        self.card_avg.config(text=self._money(avg))

    def _sort_by(self, column):
        if self.sort_state['column'] == column:
            self.sort_state['descending'] = not self.sort_state['descending']
        else:
            self.sort_state['column'] = column
            self.sort_state['descending'] = False if column not in ('amount', 'date') else True
        self._load()

    def _refresh_heading_indicators(self):
        for c in self.headings:
            arrow = ''
            if c == self.sort_state['column']:
                arrow = '  ▼' if self.sort_state['descending'] else '  ▲'
            self.tree.heading(c, text=self.headings[c] + arrow)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno('Kayıtları Sil', f'{len(sel)} adet kaydı silmek istiyor musunuz?'):
            return
        self.conn.executemany('DELETE FROM expenses WHERE id=?', [(i,) for i in sel])
        self.conn.commit()
        self._load()

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV Dosyası', '*.csv')],
            initialfile='HBS_Harcama_Raporu.csv'
        )
        if not path:
            return

        rows = self.conn.execute(
            'SELECT name, kind, amount, expense_date, method, note FROM expenses ORDER BY expense_date DESC, id DESC'
        ).fetchall()
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(['Harcama Adı', 'Harcama Türü', 'Maliyet (TL)', 'Tarih', 'Ödeme Yöntemi', 'Açıklama'])
            for r in rows:
                w.writerow([r[0], r[1], r[2], r[3], r[4] or '', r[5] or ''])
        messagebox.showinfo('Aktarım Tamamlandı', f'Rapor kaydedildi:\n{path}')

    def load_selected_to_form(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        row_id = sel[0]
        row = self.conn.execute(
            'SELECT name, kind, amount, expense_date, method, note FROM expenses WHERE id=?', (row_id,)
        ).fetchone()
        if not row:
            return
        self.vars['name'].set(row[0])
        self.vars['kind'].set(row[1])
        self.vars['amount'].set(str(row[2]).replace('.', ','))
        self.vars['date'].set(datetime.strptime(row[3], '%Y-%m-%d').strftime('%d.%m.%Y'))
        self.vars['method'].set(row[4] or '')
        self.vars['note'].set(row[5] or '')

    def on_close(self):
        try:
            self.conn.commit()
            self.conn.close()
        finally:
            self.destroy()


if __name__ == '__main__':
    app = HBSApp()
    app.protocol('WM_DELETE_WINDOW', app.on_close)
    app.mainloop()
