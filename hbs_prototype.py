import csv
import os
import shutil
import sqlite3
import sys
import tkinter as tk
from datetime import date, datetime
from tkinter import filedialog, messagebox, ttk

BG = '#118C4F'
BG_DARK = '#0D713F'
BG_LIGHT = '#EAF7F0'
WHITE = '#FFFFFF'
TEXT = '#153B2C'
MUTED = '#6D7D75'
BORDER = '#D9E5DF'


def database_path():
    """Return a writable database path for both source and PyInstaller builds."""
    if getattr(sys, 'frozen', False):
        data_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'HBS')
        os.makedirs(data_dir, exist_ok=True)
        target = os.path.join(data_dir, 'hbs_data.db')
        bundled = os.path.join(sys._MEIPASS, 'hbs_data.db')
        if not os.path.exists(target) and os.path.exists(bundled):
            shutil.copy2(bundled, target)
        return target
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hbs_data.db')


DB = database_path()


class HBSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Harcama Bilgi Sistemi • HBS 1.0')
        self.geometry('1220x760')
        self.minsize(1050, 680)
        self.configure(bg=BG_LIGHT)
        self.conn = sqlite3.connect(DB)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            kind TEXT NOT NULL,
            amount REAL NOT NULL,
            expense_date TEXT NOT NULL,
            payer TEXT,
            invoice TEXT,
            method TEXT,
            note TEXT
        )''')
        self.conn.commit()
        self.protocol('WM_DELETE_WINDOW', self._close)
        self._style()
        self._build()
        self._load()

    def _style(self):
        s = ttk.Style(self)
        s.theme_use('clam')
        s.configure('TFrame', background=BG_LIGHT)
        s.configure('Card.TFrame', background=WHITE, relief='solid', borderwidth=1)
        s.configure('TLabel', background=BG_LIGHT, foreground=TEXT, font=('Segoe UI', 10))
        s.configure('Header.TLabel', background=BG, foreground=WHITE, font=('Segoe UI', 20, 'bold'))
        s.configure('SubHeader.TLabel', background=BG, foreground='#D8F5E5', font=('Segoe UI', 10))
        s.configure('CardTitle.TLabel', background=WHITE, foreground=MUTED, font=('Segoe UI', 9, 'bold'))
        s.configure('CardValue.TLabel', background=WHITE, foreground=TEXT, font=('Segoe UI', 18, 'bold'))
        s.configure('Treeview', background=WHITE, fieldbackground=WHITE, foreground=TEXT, rowheight=34, font=('Segoe UI', 9))
        s.configure('Treeview.Heading', background=BG, foreground=WHITE, font=('Segoe UI', 9, 'bold'), padding=(8, 8))
        s.map('Treeview', background=[('selected', BG)], foreground=[('selected', WHITE)])
        s.configure('Accent.TButton', background=BG, foreground=WHITE, font=('Segoe UI', 9, 'bold'), padding=(14, 9), borderwidth=0)
        s.map('Accent.TButton', background=[('active', BG_DARK)])
        s.configure('Soft.TButton', background=WHITE, foreground=TEXT, font=('Segoe UI', 9, 'bold'), padding=(12, 9), borderwidth=1)
        s.configure('TEntry', fieldbackground=WHITE, foreground=TEXT, padding=8)
        s.configure('TCombobox', fieldbackground=WHITE, foreground=TEXT, padding=7)

    def _build(self):
        header = tk.Frame(self, bg=BG, height=106)
        header.pack(fill='x')
        tk.Label(header, text='HARCAMA BİLGİ SİSTEMİ', bg=BG, fg=WHITE, font=('Segoe UI', 23, 'bold')).pack(anchor='w', padx=28, pady=(18, 1))
        tk.Label(header, text='HBS • İşletme Harcama Kayıt ve Takip Sistemi   |   Kamacıoğlu Et Entegre', bg=BG, fg='#D8F5E5', font=('Segoe UI', 10)).pack(anchor='w', padx=30)
        tk.Label(header, text='Sürüm 1.0', bg=BG, fg='#BCE8CE', font=('Segoe UI', 9, 'bold')).pack(anchor='e', padx=28, pady=(0, 10))

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

        self.vars = {key: tk.StringVar() for key in ['name', 'kind', 'amount', 'date', 'payer', 'invoice', 'method', 'note']}
        self.vars['date'].set(date.today().strftime('%d.%m.%Y'))
        self.vars['method'].set('Banka / Havale')
        kinds = ['Yem', 'Elektrik', 'Su', 'Yakıt', 'Bakım-Onarım', 'Personel', 'Nakliye', 'Veterinerlik', 'Ekipman', 'Diğer']
        methods = ['Banka / Havale', 'Kredi Kartı', 'Nakit', 'Diğer']
        fields = [
            ('Harcama Adı *', 'name', 0, 0), ('Harcama Türü *', 'kind', 0, 2), ('Maliyet (TL) *', 'amount', 0, 4), ('Tarih', 'date', 0, 6),
            ('Firma / Ödeme Yapılan', 'payer', 1, 0), ('Fatura / Belge No', 'invoice', 1, 2), ('Ödeme Yöntemi', 'method', 1, 4), ('Açıklama', 'note', 1, 6)
        ]
        for label, key, row, column in fields:
            tk.Label(form, text=label, bg=WHITE, fg=MUTED, font=('Segoe UI', 8, 'bold')).grid(row=row * 2, column=column, sticky='w', padx=(0, 8), pady=(0, 4))
            if key == 'kind':
                widget = ttk.Combobox(form, textvariable=self.vars[key], values=kinds, state='readonly', width=18)
            elif key == 'method':
                widget = ttk.Combobox(form, textvariable=self.vars[key], values=methods, state='readonly', width=18)
            else:
                widget = ttk.Entry(form, textvariable=self.vars[key], width=21)
            widget.grid(row=row * 2 + 1, column=column, sticky='ew', padx=(0, 14), pady=(0, 7))
        for column in [1, 3, 5, 7]:
            form.columnconfigure(column, weight=1)

        buttons = tk.Frame(panel, bg=WHITE)
        buttons.pack(fill='x', padx=16, pady=(0, 14))
        ttk.Button(buttons, text='＋ Harcama Kaydet', style='Accent.TButton', command=self.add).pack(side='left')
        ttk.Button(buttons, text='Formu Temizle', style='Soft.TButton', command=self.clear_form).pack(side='left', padx=8)
        ttk.Button(buttons, text='Excel / CSV Aktar', style='Soft.TButton', command=self.export_csv).pack(side='right')
        ttk.Button(buttons, text='Seçili Kaydı Sil', style='Soft.TButton', command=self.delete_selected).pack(side='right', padx=8)

        search = tk.Frame(body, bg=BG_LIGHT)
        search.pack(fill='x', pady=(0, 8))
        tk.Label(search, text='HARCAMALAR', bg=BG_LIGHT, fg=TEXT, font=('Segoe UI', 12, 'bold')).pack(side='left')
        tk.Label(search, text='Ara:', bg=BG_LIGHT, fg=MUTED, font=('Segoe UI', 9)).pack(side='right', padx=(10, 5))
        self.q = tk.StringVar()
        ttk.Entry(search, textvariable=self.q, width=28).pack(side='right')
        self.q.trace_add('write', lambda *_: self._load())

        table_frame = tk.Frame(body, bg=WHITE, highlightthickness=1, highlightbackground=BORDER)
        table_frame.pack(fill='both', expand=True)
        columns = ('id', 'name', 'kind', 'amount', 'date', 'payer', 'invoice', 'method', 'note')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='extended')
        headings = {'id': '#', 'name': 'Harcama Adı', 'kind': 'Harcama Türü', 'amount': 'Maliyet', 'date': 'Tarih', 'payer': 'Firma / Ödeme', 'invoice': 'Belge No', 'method': 'Ödeme', 'note': 'Açıklama'}
        widths = {'id': 45, 'name': 190, 'kind': 120, 'amount': 100, 'date': 90, 'payer': 160, 'invoice': 110, 'method': 125, 'note': 230}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor='center' if column in ('id', 'amount', 'date') else 'w')
        vertical_scroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        horizontal_scroll = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vertical_scroll.set, xscrollcommand=horizontal_scroll.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vertical_scroll.grid(row=0, column=1, sticky='ns')
        horizontal_scroll.grid(row=1, column=0, sticky='ew')
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.tree.bind('<Double-1>', self.load_selected_to_form)

    def _card(self, parent, title, value):
        frame = tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground=BORDER)
        frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        tk.Label(frame, text=title, bg=WHITE, fg=MUTED, font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=15, pady=(12, 2))
        label = tk.Label(frame, text=value, bg=WHITE, fg=TEXT, font=('Segoe UI', 18, 'bold'))
        label.pack(anchor='w', padx=15, pady=(0, 12))
        return label

    def clear_form(self):
        for key in ['name', 'kind', 'amount', 'payer', 'invoice', 'note']:
            self.vars[key].set('')
        self.vars['date'].set(date.today().strftime('%d.%m.%Y'))
        self.vars['method'].set('Banka / Havale')

    def add(self):
        name = self.vars['name'].get().strip()
        kind = self.vars['kind'].get().strip()
        amount_text = self.vars['amount'].get().strip()
        if not name or not kind or not amount_text:
            messagebox.showwarning('Eksik Bilgi', 'Harcama adı, harcama türü ve maliyet alanları zorunludur.')
            return
        try:
            amount = float(amount_text.replace('.', '').replace(',', '.'))
        except ValueError:
            messagebox.showerror('Geçersiz Maliyet', 'Maliyet alanına sayısal bir değer girin.')
            return
        try:
            expense_date = datetime.strptime(self.vars['date'].get(), '%d.%m.%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Geçersiz Tarih', 'Tarih biçimi GG.AA.YYYY olmalıdır.')
            return
        self.conn.execute('INSERT INTO expenses(name,kind,amount,expense_date,payer,invoice,method,note) VALUES(?,?,?,?,?,?,?,?)', (name, kind, amount, expense_date, self.vars['payer'].get(), self.vars['invoice'].get(), self.vars['method'].get(), self.vars['note'].get()))
        self.conn.commit()
        self.clear_form()
        self._load()

    def _load(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = self.q.get().strip().lower()
        rows = self.conn.execute('SELECT id,name,kind,amount,expense_date,payer,invoice,method,note FROM expenses ORDER BY expense_date DESC,id DESC').fetchall()
        shown = []
        for row in rows:
            searchable = ' '.join('' if value is None else str(value) for value in row).lower()
            if query and query not in searchable:
                continue
            shown.append(row)
            display = list(row)
            display[3] = self._format_amount(row[3])
            display[4] = datetime.strptime(row[4], '%Y-%m-%d').strftime('%d.%m.%Y')
            self.tree.insert('', 'end', values=display)
        self._refresh_cards(shown)

    @staticmethod
    def _format_amount(value):
        return f'₺ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    def _refresh_cards(self, rows):
        total = sum(float(row[3]) for row in rows)
        now = datetime.now()
        month_total = sum(float(row[3]) for row in rows if row[4].startswith(f'{now.year:04d}-{now.month:02d}-'))
        count = len(rows)
        average = total / count if count else 0
        self.card_total.config(text=self._format_amount(total))
        self.card_month.config(text=self._format_amount(month_total))
        self.card_count.config(text=str(count))
        self.card_avg.config(text=self._format_amount(average))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        if not messagebox.askyesno('Kaydı Sil', f'{len(selected)} adet kaydı silmek istiyor musunuz?'):
            return
        ids = [self.tree.item(item, 'values')[0] for item in selected]
        self.conn.executemany('DELETE FROM expenses WHERE id=?', [(item_id,) for item_id in ids])
        self.conn.commit()
        self._load()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV Dosyası', '*.csv')], initialfile='HBS_Harcama_Raporu.csv')
        if not path:
            return
        rows = self.conn.execute('SELECT id,name,kind,amount,expense_date,payer,invoice,method,note FROM expenses ORDER BY expense_date DESC').fetchall()
        with open(path, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['ID', 'Harcama Adı', 'Harcama Türü', 'Maliyet (TL)', 'Tarih', 'Firma / Ödeme', 'Belge No', 'Ödeme Yöntemi', 'Açıklama'])
            for row in rows:
                writer.writerow(list(row))
        messagebox.showinfo('Aktarım Tamamlandı', f'Rapor kaydedildi:\n{path}')

    def load_selected_to_form(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        row = self.tree.item(selected[0], 'values')
        self.vars['name'].set(row[1])
        self.vars['kind'].set(row[2])
        self.vars['amount'].set(str(row[3]).replace('₺ ', '').replace('.', '').replace(',', '.'))
        self.vars['date'].set(row[4])
        self.vars['payer'].set(row[5])
        self.vars['invoice'].set(row[6])
        self.vars['method'].set(row[7])
        self.vars['note'].set(row[8])

    def _close(self):
        self.conn.close()
        self.destroy()


if __name__ == '__main__':
    HBSApp().mainloop()
