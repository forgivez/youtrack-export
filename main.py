import requests
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
import os
import configparser

# -------------------- 설정 관리 --------------------
CONFIG_FILE = 'config.ini'

FONT = ("\ub9c8\uae08 \uace0\ub515", 12)

# 안전하게 값 꺼내는 함수
def safe_get(obj, *keys):
    for key in keys:
        if obj and isinstance(obj, dict):
            obj = obj.get(key)
        else:
            return ''
    return obj if obj is not None else ''

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        token = config.get('YouTrack', 'token', fallback=None)
        base_url = config.get('YouTrack', 'base_url', fallback=None)
    else:
        token = None
        base_url = None

    if not token:
        token = simpledialog.askstring("토큰 입력", "YouTrack 토큰을 입력하세요:")
        if not token:
            messagebox.showerror("❌ 오류", "토큰이 입력되지 않았습니다.")
            exit()

    if not base_url:
        base_url = simpledialog.askstring("URL 입력", "YouTrack 서버 URL을 입력하세요 (ex: http://IP주소 or 도메인/api):")
        if not base_url:
            messagebox.showerror("❌ 오류", "URL이 입력되지 않았습니다.")
            exit()

    config['YouTrack'] = {'token': token, 'base_url': base_url}
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

    return token, base_url

def save_config(token, base_url):
    config = configparser.ConfigParser()
    config['YouTrack'] = {'token': token, 'base_url': base_url}
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

TOKEN, BASE_URL = load_config()

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Accept': 'application/json'
}

# -------------------- API 함수 --------------------
def fetch_issues(project_id):
    url = f"{BASE_URL}/issues"
    params = {
        'fields': 'idReadable,summary,description,created,updated,reporter(login,name),assignee(login,name),state(name),priority(name),type(name),project(shortName),tags(name),votes,commentsCount',
        'query': f'project: {project_id}',
        'top': 100,
    }
    response = requests.get(url, headers=headers, params=params, verify=False)
    response.raise_for_status()
    return response.json()

def fetch_projects():
    url = f"{BASE_URL}/admin/projects"
    params = {
        'fields': 'id,shortName,name,description,archived,fromEmail,leader(fullName,login),created,updated'
    }
    response = requests.get(url, headers=headers, params=params, verify=False)
    response.raise_for_status()
    return response.json()

# -------------------- 버튼 동작 --------------------
def on_export():
    project_id = entry_project.get().strip()
    if not project_id:
        messagebox.showwarning("⚠️ 경고", "프로젝트 ID를 입력하세요.")
        return

    try:
        issues = fetch_issues(project_id)
        if not issues:
            messagebox.showinfo("ℹ️ 알림", "가져온 이슈가 없습니다.")
            return

        df = pd.DataFrame(issues)
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="엑셀 파일로 저장"
        )
        if filepath:
            df.to_excel(filepath, index=False)
            messagebox.showinfo("✅ 완료", f"엑셀 파일로 저장 완료!\n\n{filepath}")

    except Exception as e:
        messagebox.showerror("❌ 오류", f"에러 발생:\n{e}")

def on_preview():
    project_id = entry_project.get().strip()
    if not project_id:
        messagebox.showwarning("⚠️ 경고", "프로젝트 ID를 입력하세요.")
        return

    try:
        issues = fetch_issues(project_id)
        if not issues:
            messagebox.showinfo("ℹ️ 알림", "가져온 이슈가 없습니다.")
            return

        for col in tree.get_children():
            tree.delete(col)

        for issue in issues:
            tree.insert('', 'end', values=(
                issue.get('idReadable', ''),
                issue.get('summary', ''),
                safe_get(issue, 'state', 'name'),
                safe_get(issue, 'priority', 'name'),
                safe_get(issue, 'type', 'name'),
                safe_get(issue, 'assignee', 'name'),
                safe_get(issue, 'reporter', 'name'),
                issue.get('votes', 0),
                issue.get('commentsCount', 0)
            ))

    except Exception as e:
        messagebox.showerror("❌ 오류", f"에러 발생:\n{e}")

def on_open_settings():
    settings_win = tk.Toplevel(root)
    settings_win.title("🔧 설정 변경")
    settings_win.geometry("400x200")
    settings_win.grab_set()

    tk.Label(settings_win, text="YouTrack Token:", font=FONT).pack(pady=(10,0))
    token_entry = tk.Entry(settings_win, width=50)
    token_entry.pack()
    token_entry.insert(0, TOKEN)

    tk.Label(settings_win, text="YouTrack URL:", font=FONT).pack(pady=(10,0))
    url_entry = tk.Entry(settings_win, width=50)
    url_entry.pack()
    url_entry.insert(0, BASE_URL)

    def save_settings():
        new_token = token_entry.get().strip()
        new_url = url_entry.get().strip()

        if not new_token or not new_url:
            messagebox.showerror("❌ 오류", "모든 항목을 입력하세요.")
            return

        save_config(new_token, new_url)
        messagebox.showinfo("✅ 저장 완료", "설정이 저장되었습니다. 프로그램을 다시 실행하세요.")
        settings_win.destroy()
        root.destroy()

    btn_save = tk.Button(settings_win, text="저장하고 종료", font=FONT, bg="#51cf66", fg="white", command=save_settings)
    btn_save.pack(pady=20)

def on_search_project():
    try:
        projects = fetch_projects()

        search_win = tk.Toplevel(root)
        search_win.title("📂 프로젝트 검색")
        search_win.geometry("1200x500")
        search_win.grab_set()

        tk.Label(search_win, text="검색어 (이름 포함):", font=FONT).pack(pady=(10, 0))

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_win, textvariable=search_var, font=FONT, width=40)
        search_entry.pack()

        frame_list = tk.Frame(search_win)
        frame_list.pack(fill='both', expand=True, pady=10, padx=10)

        columns = ('shortName', 'name', 'description', 'archived', 'leader', 'email', 'created', 'updated')

        tree_proj = ttk.Treeview(frame_list, columns=columns, show='headings')
        for col in columns:
            tree_proj.heading(col, text=col)
            tree_proj.column(col, width=150, anchor='w')

        tree_proj.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(frame_list, orient='vertical', command=tree_proj.yview)
        tree_proj.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        def update_treeview(keyword=""):
            tree_proj.delete(*tree_proj.get_children())
            for proj in projects:
                if keyword.lower() in proj.get('name', '').lower():
                    tree_proj.insert('', 'end', values=(
                        proj.get('shortName', ''),
                        proj.get('name', ''),
                        proj.get('description', ''),
                        '✅' if proj.get('archived') else '',
                        safe_get(proj, 'leader', 'fullName'),
                        proj.get('fromEmail', ''),
                        proj.get('created', ''),
                        proj.get('updated', '')
                    ))

        def on_select_project(event):
            selected = tree_proj.focus()
            if selected:
                proj_short_name = tree_proj.item(selected)['values'][0]
                entry_project.delete(0, tk.END)
                entry_project.insert(0, proj_short_name)
                search_win.destroy()

        search_var.trace_add('write', lambda *args: update_treeview(search_var.get()))
        tree_proj.bind('<Double-1>', on_select_project)

        update_treeview()

    except Exception as e:
        messagebox.showerror("❌ 오류", f"프로젝트 검색 실패:\n{e}")

# -------------------- UI --------------------
root = tk.Tk()
root.title("🎯 YouTrack 이슈 엑셀 추출기")
root.geometry("1100x750")
root.configure(bg='#f8f9fa')

menubar = tk.Menu(root)
menu_settings = tk.Menu(menubar, tearoff=0)
menu_settings.add_command(label="🔧 설정 변경", command=on_open_settings)
menubar.add_cascade(label="설정", menu=menu_settings)
root.config(menu=menubar)

frame_top = tk.Frame(root, bg='#f8f9fa', pady=20)
frame_top.pack(fill='x')

label_project = tk.Label(frame_top, text="프로젝트 ID:", font=FONT, bg='#f8f9fa')
label_project.pack(side='left', padx=(20, 10))

entry_project = tk.Entry(frame_top, width=30, font=FONT)
entry_project.pack(side='left')

status_var = tk.StringVar()
combo_status = ttk.Combobox(frame_top, textvariable=status_var, state='readonly', font=FONT, width=10)
combo_status['values'] = ('전체', 'Open', 'In Progress', 'Fixed', 'Closed', 'Resolved')
combo_status.current(0)
combo_status.pack(side='left', padx=(20, 10))

frame_buttons = tk.Frame(root, bg='#f8f9fa', pady=10)
frame_buttons.pack()

btn_preview = tk.Button(frame_buttons, text="🔎 미리보기", font=FONT, width=15, bg='#4dabf7', fg='white', command=on_preview)
btn_preview.pack(side='left', padx=10)

btn_export = tk.Button(frame_buttons, text="💾 엑셀로 저장", font=FONT, width=15, bg='#51cf66', fg='white', command=on_export)
btn_export.pack(side='left', padx=10)

btn_search_project = tk.Button(frame_buttons, text="📂 프로젝트 검색", font=FONT, width=18, bg='#ffa94d', fg='white', command=on_search_project)
btn_search_project.pack(side='left', padx=10)

frame_preview = tk.Frame(root, bg='#f8f9fa', pady=10)
frame_preview.pack(fill='both', expand=True)

tree = ttk.Treeview(frame_preview, columns=('이슈 ID', '제목', '상태', '우선순위', '유형', '담당자', '작성자', '투표수', '댓글수'), show='headings')
tree.heading('이슈 ID', text='이슈 ID')
tree.heading('제목', text='제목')
tree.heading('상태', text='상태')
tree.heading('우선순위', text='우선순위')
tree.heading('유형', text='유형')
tree.heading('담당자', text='담당자')
tree.heading('작성자', text='작성자')
tree.heading('투표수', text='투표수')
tree.heading('댓글수', text='댓글수')

for col in tree['columns']:
    tree.column(col, anchor='center', width=100)

tree.pack(fill='both', expand=True, padx=20, pady=10)

root.mainloop()
