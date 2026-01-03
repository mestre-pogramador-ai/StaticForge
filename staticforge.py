import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import json
import os
import shutil
from datetime import datetime
import re
import subprocess
import stat

# Arquivos de dados
POSTS_FILE = "posts.json"
PAGES_FILE = "pages.json"
CONFIG_FILE = "config.json"

# Funções de carregamento
def load_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_posts(posts):
    with open(POSTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=4, ensure_ascii=False)

def load_pages():
    if os.path.exists(PAGES_FILE):
        with open(PAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_pages(pages):
    with open(PAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(pages, f, indent=4, ensure_ascii=False)

def load_config():
    default = {
        "name": "StaticForge",
        "description": "Site gerado com StaticForge",
        "github_repo": "",
        "github_token": "",
        "github_branch": "main",
        "base_url": "",
        "image_size": "Original"
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            default.update(data)
    return default

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

class App(ttkb.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("StaticForge - Gerador de Site Estático")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        self.posts = load_posts()
        self.pages = load_pages()
        self.config = load_config()

        self.setup_ui()
        self.update_all_lists()

    def _handle_remove_readonly(self, func, path, exc_info):
        import stat
        # Tenta mudar as permissões do arquivo para permitir a exclusão no Windows
        if not os.path.exists(path):
            return # Arquivo já foi removido por outra chamada recursiva
        
        if func in (os.rmdir, os.remove, os.unlink):
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception as e:
                # Se falhar novamente, levanta a exceção original
                raise e
        else:
            raise exc_info[1] # Levanta a exceção original para outros erros



    def setup_ui(self):
        header = ttkb.Frame(self, padding=30)
        header.pack(fill=X)

        ttkb.Label(header, text="StaticForge", font=("Helvetica", 32, "bold"), foreground="#3498db").pack()
        ttkb.Label(header, text="Gerenciador completo com publicação automática no GitHub Pages",
                  font=("Helvetica", 12), foreground="#95a5a6").pack(pady=(10, 30))

        buttons_frame = ttkb.Frame(self)
        buttons_frame.pack(fill=X, pady=20)

        ttkb.Button(buttons_frame, text="➕ Novo Post", bootstyle=SUCCESS, width=18,
                   command=lambda: self.create_content("post")).grid(row=0, column=0, padx=15)
        ttkb.Button(buttons_frame, text="📄 Nova Página", bootstyle=INFO, width=18,
                   command=lambda: self.create_content("page")).grid(row=0, column=1, padx=15)
        ttkb.Button(buttons_frame, text="✏️ Editar", bootstyle=PRIMARY, width=18,
                   command=self.edit_content).grid(row=0, column=2, padx=15)
        ttkb.Button(buttons_frame, text="🚀 Publicar", bootstyle=WARNING, width=18,
                   command=self.publish_content).grid(row=0, column=3, padx=15)
        ttkb.Button(buttons_frame, text="⚙️ Configurações", bootstyle=SECONDARY, width=18,
                   command=self.configure).grid(row=0, column=4, padx=15)
        ttkb.Button(buttons_frame, text="🌐 Gerar Site", bootstyle=(SUCCESS, OUTLINE), width=25,
                   command=self.generate_static_site).grid(row=0, column=5, padx=15)

        self.notebook = ttkb.Notebook(self, bootstyle="dark")
        self.notebook.pack(fill=BOTH, expand=True, padx=40, pady=30)

        self.posts_frame = ttkb.Frame(self.notebook)
        self.pages_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.posts_frame, text="   📝 Posts do Blog   ")
        self.notebook.add(self.pages_frame, text="   📃 Páginas Fixas   ")

        self.setup_list(self.posts_frame, "post")
        self.setup_list(self.pages_frame, "page")

    def setup_list(self, frame, content_type):
        ttkb.Label(frame, text=f"{content_type.capitalize()}s", font=("Helvetica", 16, "bold")).pack(pady=20)

        listbox = tk.Listbox(frame, font=("Consolas", 11), height=22, bg="#2c3e50", fg="white",
                            selectbackground="#3498db", highlightthickness=0, bd=0)
        listbox.pack(fill=BOTH, expand=True, padx=50)

        scrollbar = ttkb.Scrollbar(frame, orient=VERTICAL, command=listbox.yview, bootstyle="round")
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        if content_type == "post":
            self.post_listbox = listbox
        else:
            self.page_listbox = listbox

    def update_list(self, listbox, items):
        listbox.delete(0, tk.END)
        for item in items:
            status = "Publicado" if item.get('published', False) else "Rascunho"
            color = "#27ae60" if item.get('published', False) else "#f39c12"
            tags = ", ".join(item.get('tags', []))
            cat = item.get('category', 'Sem categoria')
            imgs = len(item.get('images', []))
            extra = f" | {cat}"
            if tags: extra += f" | {tags}"
            if imgs: extra += f" | {imgs} img{'s' if imgs != 1 else ''}"
            listbox.insert(tk.END, f"{item['title']} — {status}{extra}")
            listbox.itemconfig(tk.END, fg=color)

    def update_all_lists(self):
        self.update_list(self.post_listbox, self.posts)
        self.update_list(self.page_listbox, self.pages)

    def create_content(self, ctype):
        self.content_window(f"Novo {ctype.capitalize()}", {}, ctype)

    def edit_content(self):
        tab = self.notebook.select()
        text = self.notebook.tab(tab, "text")
        listbox = self.post_listbox if "Posts" in text else self.page_listbox
        items = self.posts if "Posts" in text else self.pages
        ctype = "post" if "Posts" in text else "page"

        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("Seleção", "Selecione um item para editar.")
            return
        self.content_window("Editar", items[sel[0]], ctype, sel[0])

    def content_window(self, title, item, ctype, index=None):
        win = ttkb.Toplevel(title=f"{title} {ctype.capitalize()} - StaticForge")
        win.geometry("1100x900")

        canvas = tk.Canvas(win)
        scrollbar = ttkb.Scrollbar(win, orient=VERTICAL, command=canvas.yview)
        frame = ttkb.Frame(canvas)
        canvas.create_window((0,0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        entries = {}
        row = 0
        for label, key in [("Título", "title"), ("Descrição", "description"), ("Categoria", "category")]:
            ttkb.Label(frame, text=label + ":", font=("Helvetica", 12, "bold")).grid(row=row, column=0, sticky=W, pady=12, padx=30)
            entry = ttkb.Entry(frame, width=90)
            entry.grid(row=row, column=1, pady=12, padx=30)
            value = item.get(key, '')
            if key == "category" and not value: value = "Sem categoria"
            entry.insert(0, value)
            entries[key] = entry
            row += 1

        ttkb.Label(frame, text="Tags (vírgula):", font=("Helvetica", 12, "bold")).grid(row=row, column=0, sticky=W, pady=12, padx=30)
        tags_entry = ttkb.Entry(frame, width=90)
        tags_entry.grid(row=row, column=1, pady=12, padx=30)
        tags_entry.insert(0, ", ".join(item.get('tags', [])))
        row += 1

        ttkb.Label(frame, text="Conteúdo (HTML OK):", font=("Helvetica", 12, "bold")).grid(row=row, column=0, sticky=NW, pady=12, padx=30)
        content = tk.Text(frame, height=18, width=90, font=("Consolas", 11))
        content.grid(row=row, column=1, pady=12, padx=30)
        content.insert("end", item.get('content', ''))
        row += 1

        current_images = item.get('images', []).copy()
        img_frame = ttkb.Frame(frame)
        img_frame.grid(row=row, column=1, sticky=W, pady=20, padx=30)

        def refresh_images():
            for w in img_frame.winfo_children(): w.destroy()
            for path in current_images:
                if not os.path.exists(path): continue
                rowf = ttkb.Frame(img_frame)
                rowf.pack(fill=X, pady=4)
                try:
                    img = Image.open(path).resize((100,100))
                    photo = ImageTk.PhotoImage(img)
                    ttkb.Label(rowf, image=photo).pack(side=LEFT, padx=10)
                    rowf.image = photo
                except: pass
                ttkb.Label(rowf, text=os.path.basename(path)).pack(side=LEFT, padx=10)
                ttkb.Button(rowf, text="✕", bootstyle=DANGER, width=3,
                           command=lambda p=path: (current_images.remove(p), refresh_images())).pack(side=LEFT)

        def add_imgs():
            files = filedialog.askopenfilenames(title="Selecionar imagens")
            if files: current_images.extend(files); refresh_images()

        ttkb.Label(frame, text="Imagens:", font=("Helvetica", 12, "bold")).grid(row=row, column=0, sticky=W, pady=20, padx=30)
        ttkb.Button(frame, text="Adicionar Imagens", bootstyle=INFO, command=add_imgs).grid(row=row+1, column=1, sticky=W, padx=30, pady=10)
        refresh_images()
        row += 2

        btn_frame = ttkb.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=50)

        def save():
            tags = [t.strip() for t in tags_entry.get().split(",") if t.strip()]
            new_item = {
                'title': entries['title'].get(),
                'description': entries['description'].get(),
                'category': entries['category'].get().strip() or "Sem categoria",
                'tags': tags,
                'content': content.get("1.0", "end").strip(),
                'images': current_images.copy(),
                'published': item.get('published', False)
            }
            items = self.posts if ctype == "post" else self.pages
            if index is None:
                items.append(new_item)
            else:
                items[index] = new_item
            (save_posts if ctype == "post" else save_pages)(items)
            self.update_all_lists()
            win.destroy()
            messagebox.showinfo("Sucesso", "Salvo com sucesso!")

        def delete():
            if messagebox.askyesno("Deletar?", "Tem certeza?"):
                items = self.posts if ctype == "post" else self.pages
                items.pop(index)
                (save_posts if ctype == "post" else save_pages)(items)
                self.update_all_lists()
                win.destroy()

        ttkb.Button(btn_frame, text="💾 Salvar", bootstyle=SUCCESS, width=20, command=save).pack(side=LEFT, padx=100)
        if index is not None:
            ttkb.Button(btn_frame, text="🗑️ Deletar", bootstyle=DANGER, width=20, command=delete).pack(side=RIGHT, padx=100)

    def publish_content(self):
        tab = self.notebook.select()
        text = self.notebook.tab(tab, "text")
        listbox = self.post_listbox if "Posts" in text else self.page_listbox
        items = self.posts if "Posts" in text else self.pages

        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um item.")
            return
        items[sel[0]]['published'] = True
        (save_posts if "Posts" in text else save_pages)(items)
        self.update_all_lists()
        messagebox.showinfo("Publicado", "Conteúdo publicado!")

    def configure(self):
        win = ttkb.Toplevel("Configurações")
        win.geometry("700x500")

        notebook = ttkb.Notebook(win)
        notebook.pack(fill=BOTH, expand=True, padx=20, pady=20)

        geral = ttkb.Frame(notebook)
        notebook.add(geral, text="Geral")

        ttkb.Label(geral, text="Nome do Site", font=("Helvetica", 14)).pack(pady=(30,10), anchor=W, padx=50)
        name_e = ttkb.Entry(geral, width=60)
        name_e.pack(pady=10, padx=50)
        name_e.insert(0, self.config.get('name', 'StaticForge'))

        ttkb.Label(geral, text="Descrição do Site").pack(pady=(30,5), anchor=W, padx=50)
        desc_e = ttkb.Entry(geral, width=60)
        desc_e.pack(pady=10, padx=50)
        desc_e.insert(0, self.config.get('description', ''))

        ttkb.Label(geral, text="URL Base do Site (ex: https://meusite.com/)", font=("Helvetica", 12)).pack(pady=(30,5), anchor=W, padx=50)
        base_url_e = ttkb.Entry(geral, width=60)
        base_url_e.pack(pady=10, padx=50)
        base_url_e.insert(0, self.config.get('base_url', ''))

        ttkb.Label(geral, text="Tamanho Padrão das Imagens (Postagens)", font=("Helvetica", 12)).pack(pady=(30,5), anchor=W, padx=50)
        image_sizes = ["Original", "800x500", "600x400", "400x300"]
        size_var = tk.StringVar(value=self.config.get('image_size', 'Original'))
        size_combo = ttkb.Combobox(geral, textvariable=size_var, values=image_sizes, state="readonly", width=20)
        size_combo.pack(pady=10, padx=50)

        github = ttkb.Frame(notebook)
        notebook.add(github, text="GitHub")

        ttkb.Label(github, text="URL do Repositório GitHub", font=("Helvetica", 12)).pack(pady=(30,5), anchor=W, padx=50)
        repo_e = ttkb.Entry(github, width=70)
        repo_e.pack(pady=5, padx=50)
        repo_e.insert(0, self.config.get('github_repo', ''))

        ttkb.Label(github, text="Personal Access Token (recomendado)", font=("Helvetica", 12)).pack(pady=(20,5), anchor=W, padx=50)
        token_e = ttkb.Entry(github, width=70, show="*")
        token_e.pack(pady=5, padx=50)
        token_e.insert(0, self.config.get('github_token', ''))

        ttkb.Label(github, text="Branch (geralmente 'main')").pack(pady=(20,5), anchor=W, padx=50)
        branch_e = ttkb.Entry(github, width=30)
        branch_e.pack(pady=5, padx=50)
        branch_e.insert(0, self.config.get('github_branch', 'main'))

        def test_connection():
            repo = repo_e.get().strip()
            token = token_e.get().strip()
            if not repo:
                messagebox.showwarning("Erro", "Preencha a URL do repositório.")
                return
            try:
                auth = f"{token}@" if token else ""
                test_url = repo.replace("https://", f"https://{auth}")
                result = subprocess.run(["git", "ls-remote", test_url], capture_output=True, text=True)
                if result.returncode == 0:
                    messagebox.showinfo("Sucesso!", "Conexão com GitHub OK! Pode publicar.")
                else:
                    messagebox.showerror("Falha", "Não foi possível conectar.\nVerifique URL e token.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao testar:\n{str(e)}")

        ttkb.Button(github, text="Testar Conexão GitHub", bootstyle=SUCCESS, command=test_connection).pack(pady=30)

        def save():
            self.config.update({
                'name': name_e.get(),
                'description': desc_e.get(),
                'base_url': base_url_e.get().strip(),
                'image_size': size_var.get(),
                'github_repo': repo_e.get().strip(),
                'github_token': token_e.get(),
                'github_branch': branch_e.get().strip() or "main"
            })
            save_config(self.config)
            win.destroy()
            messagebox.showinfo("OK", "Configurações salvas com sucesso!")

        ttkb.Button(win, text="Salvar Tudo", bootstyle=SUCCESS, command=save).pack(pady=20)

    def slugify(self, text):
        text = re.sub(r'[^\w\s-]', '', text.lower())
        return re.sub(r'[-\s]+', '-', text).strip('-')

    def generate_static_site(self):
        published_posts = [p for p in self.posts if p.get('published', False)]
        published_pages = [p for p in self.pages if p.get('published', False)]
        all_content = published_posts + published_pages

        if not all_content:
            messagebox.showwarning("Nada para gerar", "Publique pelo menos um post ou página.")
            return

        result = messagebox.askyesnocancel("Publicar no GitHub?",
            "O que deseja fazer?\n\n"
            "Sim → Gerar e publicar no GitHub Pages\n"
            "Não → Apenas gerar localmente\n"
            "Cancelar → Voltar")

        if result is None:
            return

        publish_github = (result == True)

        if publish_github and not self.config.get('github_repo'):
            messagebox.showwarning("Configuração necessária", "Configure o GitHub em Configurações antes de publicar.")
            return

        prog = ttkb.Toplevel("Gerando...")
        prog.geometry("500x200")
        ttkb.Label(prog, text="Gerando site estático...\nAguarde alguns segundos", font=("Helvetica", 12)).pack(pady=40)
        bar = ttkb.Progressbar(prog, mode="indeterminate", bootstyle=SUCCESS)
        bar.pack(fill=X, padx=80, pady=20)
        bar.start()

        base_url = self.config.get('base_url', '').rstrip('/')
        home_link = base_url if base_url else 'index.html'
        self.after(100, lambda: self._generate_and_publish(published_posts, published_pages, all_content, prog, publish_github, home_link))

    def _generate_and_publish(self, published_posts, published_pages, all_content, prog_win, publish_github, home_link):
        site_dir = "site"
        posts_dir = os.path.join(site_dir, "posts")
        images_dir = os.path.join(site_dir, "images")

        if os.path.exists(site_dir):
            shutil.rmtree(site_dir, onerror=self._handle_remove_readonly)
        os.makedirs(site_dir)
        os.makedirs(posts_dir)
        os.makedirs(images_dir)

        copied_images = {}
        image_size_config = self.config.get('image_size', 'Original')
        
        # Lógica para obter as dimensões
        size = None
        if image_size_config != "Original":
            try:
                w, h = map(int, image_size_config.split('x'))
                size = (w, h)
            except ValueError:
                pass # Fallback to original size if format is invalid
        
        for item in all_content:
            for path in item.get('images', []):
                if os.path.exists(path):
                    fname = os.path.basename(path)
                    dest = os.path.join(images_dir, fname)
                    
                    if not os.path.exists(dest):
                        # Se o tamanho for definido, redimensiona a imagem
                        if size:
                            try:
                                from PIL import Image
                                img = Image.open(path)
                                img = img.resize(size)
                                img.save(dest)
                            except Exception as e:
                                # Em caso de erro (ex: formato inválido), copia o original
                                shutil.copy2(path, dest)
                        else:
                            # Se for Original, apenas copia
                            shutil.copy2(path, dest)
                            
                    copied_images[path] = fname

        # Dados para busca
        search_data = []
        for item in all_content:
            search_data.append({
                'title': item['title'],
                'description': item.get('description', ''),
                'content': item['content'],
                'category': item.get('category', 'Sem categoria'),
                'tags': item.get('tags', []),
                'slug': self.slugify(item['title'])
            })
        search_js = f"const searchData = {json.dumps(search_data, ensure_ascii=False)};"

        # Template HTML
        html_head = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg: #ffffff; --text: #222; --card: #f8f9fa; --accent: #3498db; }}
        @media (prefers-color-scheme: dark) {{ :root {{ --bg: #1a1a1a; --text: #e0e0e0; --card: #242424; --accent: #5dafeb; }} }}
        body {{ font-family: 'Inter', sans-serif; margin:0; background:var(--bg); color:var(--text); transition:0.3s; }}
        header {{ background:linear-gradient(135deg,#2c3e50,#3498db); color:white; padding:3rem 1rem; text-align:center; }}
        .search {{ max-width:600px; margin:2rem auto; }}
        .search input {{ width:100%; padding:1rem; font-size:1.1rem; border-radius:50px; border:none; box-shadow:0 4px 15px rgba(0,0,0,0.2); }}
        nav {{ background:rgba(0,0,0,0.1); padding:1rem; text-align:center; }}
        nav a {{ color:white; margin:0 1.5rem; text-decoration:none; font-weight:600; }}
        .container {{ max-width:1100px; margin:2rem auto; padding:0 1rem; }}
        .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:2rem; }}
        .card {{ background:var(--card); border-radius:16px; overflow:hidden; box-shadow:0 10px 30px rgba(0,0,0,0.1); transition:0.3s; }}
        .card:hover {{ transform:translateY(-10px); }}
        .card img {{ width:100%; height:200px; object-fit:cover; }}
        .card-content {{ padding:1.5rem; }}
        .tags {{ font-size:0.9rem; color:var(--accent); }}
        footer {{ text-align:center; padding:3rem; background:#2c3e50; color:white; }}
        .dark-toggle {{ position:fixed; bottom:30px; right:30px; background:var(--accent); color:white; border:none; width:56px; height:56px; border-radius:50%; font-size:28px; cursor:pointer; box-shadow:0 6px 20px rgba(0,0,0,0.3); z-index:100; }}
    </style>
    <script>
        {search_js}
        function search() {{
            let q = document.getElementById('q').value.toLowerCase().trim();
            let res = document.getElementById('results');
            let grid = document.getElementById('grid');
            if (!q) {{ res.innerHTML=''; grid.style.display='grid'; return; }}
            grid.style.display='none';
            let html = '<h2>Resultados:</h2><div class="grid">';
            let n = 0;
            searchData.forEach(i => {{
                if ((i.title+' '+i.description+' '+i.content+' '+i.category+' '+i.tags.join(' ')).toLowerCase().includes(q)) {{
                    n++;
                    let img = i.images && i.images.length ? `<img src="images/${{i.images[0]}}">` : '';
                    html += `<div class="card">${{img}}<div class="card-content"><h3><a href="posts/${{i.slug}}.html">${{i.title}}</a></h3><p class="tags">Cat: ${{i.category}} | Tags: ${{i.tags.join(', ')}}</p><p>${{i.description}}</p></div></div>`;
                }}
            }});
            html += n ? '</div>' : '<p>Nada encontrado.</p>';
            res.innerHTML = html;
        }}
        function toggleDark() {{ document.body.classList.toggle('forced-dark'); }}
    </script>
</head>
<body>
	    <header>
	        <h1>{site_name}</h1>
	        <p>{site_desc}</p>
	        <div class="search"><input type="text" id="q" placeholder="Buscar..." onkeyup="search()"></div>
	    </header>
	    <nav><a href="{home_link}">Início</a>{nav_links}</nav>
    <button class="dark-toggle" onclick="toggleDark()">🌙</button>
    <div id="results"></div>
"""

        site_name = self.config.get('name', 'StaticForge')
        site_desc = self.config.get('description', '')
        nav_links = " | " + " | ".join([f'<a href="posts/{self.slugify(p["title"])}.html">{p["title"]}</a>' for p in published_pages]) if published_pages else ""

        # Index
        index_html = html_head.format(title=site_name, site_name=site_name, site_desc=site_desc, nav_links=nav_links, search_js=search_js, home_link=home_link) + """
    <div class="container">
        <div id="grid" class="grid">
"""
        for post in reversed(published_posts):
            slug = self.slugify(post['title'])
            img = f'<img src="images/{copied_images.get(post["images"][0], "")}">' if post.get('images') else ""
            tags = f'<p class="tags">Tags: {", ".join(post.get("tags", []))}</p>' if post.get('tags') else ""
            index_html += f"""
            <div class="card">
                {img}
                <div class="card-content">
                    <h3><a href="posts/{slug}.html">{post['title']}</a></h3>
                    <p class="tags">Categoria: {post.get('category', 'Sem categoria')}</p>
                    {tags}
                    <p>{post.get('description', '')}</p>
                </div>
            </div>
"""
        index_html += """
        </div>
    </div>
    <footer><p>Gerado com <strong>StaticForge</strong></p></footer>
</body></html>
"""
        with open(os.path.join(site_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(index_html)

        # Páginas individuais
        for item in all_content:
            slug = self.slugify(item['title'])
            imgs = "".join(f'<img src="../images/{copied_images.get(p, "")}">' for p in item.get('images', []) if copied_images.get(p))
            content = item['content'].replace("\n", "<br>")
            tags = f'<p class="tags">Tags: {", ".join(item.get("tags", []))}</p>' if item.get('tags') else ""
            page_html = html_head.format(title=f"{item['title']} - {site_name}", site_name=site_name, site_desc=site_desc, nav_links=nav_links, search_js=search_js, home_link=home_link) + f"""
    <div class="container">
        <h2>{item['title']}</h2>
        <p class="tags">Categoria: {item.get('category', 'Sem categoria')}</p>
        {tags}
        <p><em>{item.get('description', '')}</em></p>
        <div style="display:flex;flex-wrap:wrap;gap:1.5rem;justify-content:center;margin:3rem 0;">{imgs}</div>
	        <div style="font-size:1.1em;line-height:1.9;">{content}</div>
	        <p style="margin:4rem 0;"><a href="{home_link}">← Voltar</a></p>
    </div>
    <footer><p>Gerado com <strong>StaticForge</strong></p></footer>
</body></html>
"""
            with open(os.path.join(posts_dir, f"{slug}.html"), "w", encoding="utf-8") as f:
                f.write(page_html)

        prog_win.destroy()

        if publish_github:
            self.publish_to_github(site_dir)
        else:
            messagebox.showinfo("Concluído", f"Site gerado na pasta 'site'!\nAbra site/index.html")

    def publish_to_github(self, site_dir):
        repo_url = self.config.get('github_repo', '').strip()
        token = self.config.get('github_token', '').strip()
        branch = self.config.get('github_branch', 'main').strip()

        if not repo_url:
            messagebox.showerror("Erro", "URL do repositório não configurada em Configurações.")
            return

        try:
            # Monta URL com token
            if token:
                auth_url = repo_url.replace("https://", f"https://{token}@")
            else:
                auth_url = repo_url
                messagebox.showwarning("Aviso", "Você não configurou um token. Pode falhar em repositórios privados.")

            repo_path = site_dir

            # Inicializa git
            if not os.path.exists(os.path.join(repo_path, ".git")):
                subprocess.run(["git", "init"], cwd=repo_path, check=True)
                # Garante que o branch local seja o configurado (main por padrão)
                subprocess.run(["git", "checkout", "-b", branch], cwd=repo_path, check=True)
            else:
                # Se já existe, apenas garante que estamos no branch correto
                subprocess.run(["git", "checkout", branch], cwd=repo_path, check=True)

            # Remove remote antigo
            subprocess.run(["git", "remote", "remove", "origin"], cwd=repo_path, capture_output=True)

            # Tenta adicionar o remote
            add_result = subprocess.run(["git", "remote", "add", "origin", auth_url], 
                                       cwd=repo_path, capture_output=True, text=True)

            if add_result.returncode != 0:
                if "fatal: repository" in add_result.stderr.lower() or "not found" in add_result.stderr.lower():
                    messagebox.showerror("Repositório não encontrado",
                        "O repositório GitHub não existe ou está com nome errado.\n\n"
                        "Verifique:\n"
                        f"- URL: {repo_url}\n"
                        "- Se o repositório foi criado no GitHub\n"
                        "- Se está público (ou token tem acesso)")
                elif "authentication failed" in add_result.stderr.lower():
                    messagebox.showerror("Token inválido", "O token está errado ou não tem permissão 'repo'.")
                else:
                    messagebox.showerror("Erro no remote", f"Não foi possível adicionar o remote:\n{add_result.stderr}")
                return

            # Configura usuário
            subprocess.run(["git", "config", "user.name", "StaticForge"], cwd=repo_path, check=True)
            subprocess.run(["git", "config", "user.email", "staticforge@auto"], cwd=repo_path, check=True)

            # Commit e push
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            commit_result = subprocess.run(["git", "commit", "-m", "Update automático"], cwd=repo_path, capture_output=True, text=True)
            if commit_result.returncode != 0 and "nothing to commit" not in commit_result.stdout:
                messagebox.showwarning("Nada para commit", "Nenhuma alteração detectada.")
                return

            # Tenta o push, forçando a criação do branch remoto se necessário
            push_result = subprocess.run(["git", "push", "--force", "--set-upstream", "origin", branch], 
                                       cwd=repo_path, capture_output=True, text=True)

            if push_result.returncode == 0:
                live_url = repo_url.replace(".git", "").replace("https://github.com/", "https://")
                messagebox.showinfo("SUCESSO TOTAL! 🎉",
                    f"Seu site foi publicado com sucesso!\n\n"
                    f"Acesse em até 1 minuto:\n{live_url}\n\n"
                    f"Atualize sempre que quiser com um clique!")
            else:
                messagebox.showerror("Erro no push", f"Falha no push:\n{push_result.stderr}")

        except Exception as e:
            messagebox.showerror("Erro inesperado", f"{str(e)}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
