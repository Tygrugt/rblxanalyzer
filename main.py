import os, io, re, sys, math, json, shutil, tkinter, datetime, requests
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

######################################################### BASE FUNCTIONS #########################################################
def ShowMessage(type="info", title="RBLX ANALYZER", info="..."):
    if type == "warning":
        messagebox.showwarning(title, info)
    elif type == "error":
        messagebox.showerror(title, info)
    elif type == "info":
        messagebox.showinfo(title, info)

def OpenWindow(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.resizable(False, False)

############################################################ ID CHECK ############################################################
def CheckInternetConnection():
    try:
        response = requests.head("https://www.google.com/", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        ShowMessage(type = "error", info = "No Internet Connection")
        return False

def CheckRobloxConnection():
    if CheckInternetConnection():
        try:
            response = requests.head("https://www.roblox.com/", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            ShowMessage(type = "error", info = "No Roblox API Server Connection")
            return False

def GetUniverseId(id):
    if CheckRobloxConnection():
        unid = None
        place_url = f"https://apis.roblox.com/universes/v1/places/{id}/universe"
        universe_url = f"https://games.roblox.com/v1/games?universeIds={id}"

        place_response = requests.get(place_url)
        universe_response = requests.get(universe_url)

        place_succes = False
        universe_succes = False

        if place_response.status_code == 200:
            place_data = place_response.json()
            if "universeId" in place_data and place_data["universeId"]:
                place_succes = True

        if universe_response.status_code == 200 and unid is None:
            universe_data = universe_response.json()
            if "data" in universe_data and len(universe_data["data"]) > 0:
                place_succes = True
        
        if place_succes == True and universe_succes == False:
            unid = place_data["universeId"]
        elif place_succes == False and universe_succes == True:
            unid = id
        else:
            unid = place_data["universeId"]
        print(unid)
        return unid
    
######################################################### FILES CREATION #########################################################
def CreateBasePaths():
    if not os.path.exists("data"):
        os.makedirs("data", exist_ok=True)
    if not os.path.exists("data\\games"):
        os.makedirs("data\\games", exist_ok=True)
    if not os.path.exists("data\\groups"):
        os.makedirs("data\\groups", exist_ok=True)
    if not os.path.exists("data\\players"):
        os.makedirs("data\\players", exist_ok=True)
    if not os.path.exists("saved.json"):
        with open("saved.json", "w", encoding="utf-8") as json_file:
            json.dump({}, json_file, indent=4)
    if not os.path.exists("config.json"):
        with open("config.json", "w", encoding="utf-8") as json_file:
            json.dump({}, json_file, indent=4)

########################################################### SAVED CONTROL ###########################################################
saved_data = {}

def LoadFromSaved():
    global saved_data
    with open("saved.json", "r", encoding="utf-8") as json_file:
        saved_data = json.load(json_file)
        sorted_saved_data = dict(sorted(saved_data.items()))
        saved_data = sorted_saved_data
    print(saved_data)
    return saved_data

def UploadToSaved():
    global saved_data
    with open("saved.json", "w", encoding="utf-8") as json_file:
        json.dump(saved_data, json_file, indent=4)
    return saved_data

def AddSaved(name:str, id:int):
    global saved_data
    LoadFromSaved()
    if name.lower() not in map(str.lower, saved_data.keys()):
        if GetUniverseId(id) != None and GetUniverseId(id) not in saved_data.values():
            saved_data[name] = GetUniverseId(id)
            sorted_saved_data = dict(sorted(saved_data.items()))
            saved_data = sorted_saved_data
            try:
                if not os.path.exists(f"data\\games\\{name}"):
                    os.makedirs(f"data\\games\\{name}", exist_ok=True)
                if not os.path.exists(f"data\\games\\{name}\\basedata"):
                    os.makedirs(f"data\\games\\{name}\\basedata", exist_ok=True)
                if not os.path.exists(f"data\\games\\{name}\\images"):
                    os.makedirs(f"data\\games\\{name}\\images", exist_ok=True)
                UploadToSaved()
                UpdateList()
            except:
                ShowMessage(type = "error", info = "Invalid save name: This name was rejected by the system")
                return
        else:
            ShowMessage(type = "error", info = "Invalid ID: Incorrect ID, Empty ID or ID already exist")
            return
    else:
        ShowMessage(type = "error", info = "Invalid save name: This name already exist")
        return

def DelSaved(name):
    global saved_data
    LoadFromSaved()
    if name in saved_data.keys():
        del saved_data[name]
        sorted_saved_data = dict(sorted(saved_data.items()))
        saved_data = sorted_saved_data
        UploadToSaved()
        if os.path.exists(f"data\\games\\{name}"):
            shutil.rmtree(f"data\\games\\{name}")
        UpdateList()

def UpdateList():
    LoadFromSaved()
    for item in gamesList.get_children():
        gamesList.delete(item)
    for i, v in saved_data.items():
        gamesList.insert("", tkinter.END, values=("-", i, v))
    for index, item_id in enumerate(gamesList.get_children()):
        gamesList.item(item_id, values=(index + 1, gamesList.item(item_id, "values")[1], gamesList.item(item_id, "values")[2]))

def DelFromList():
    selectedItem = gamesList.focus()
    if not selectedItem:
        return
    values = gamesList.item(selectedItem, "values")
    game_name = values[1]
    DelSaved(game_name)

    
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
########################################################### INPUT ID ###########################################################

def OpedIdInputWindow():
    id_input_window = tkinter.Toplevel(root)
    id_input_window.title("RBLX Analyzer")
    icon_path = resource_path("assets\\icon.ico")
    id_input_window.iconbitmap(icon_path)
    OpenWindow(id_input_window, 250, 90)
    digitvalid = (id_input_window.register(CheckIdValidation), "%d", "%P")
    idInputFrame = ttk.Frame(id_input_window)
    submitIdButton = ttk.Button(idInputFrame, text="OK", command = lambda: CloseIdInputWindow(id_input_window, nameEntry.get(), idEntry.get()))
    idEntry = ttk.Entry(idInputFrame, validate="key", validatecommand=digitvalid)
    nameEntry = ttk.Entry(idInputFrame)
    idInputTip = ttk.Label(idInputFrame, text="Enter game ID:")
    nameInputTip = ttk.Label(idInputFrame, text="Enter a save name:")
    idInputFrame.place(relwidth=1, relheight=1)
    idInputTip.place(relx=0.05, rely=0.1)
    nameInputTip.place(relx=0.05, rely=0.4)
    idEntry.place(relx=0.5, rely=0.1, relwidth=0.45)
    nameEntry.place(relx=0.5, rely=0.4, relwidth=0.45)
    submitIdButton.place(relx=0.5, rely=0.98, anchor="s")
    id_input_window.grab_set()
    root.wait_window(id_input_window)

info_window = None
open_graph_windows = []
def OpedInfoWindow(saved_name):
    global root
    global info_window
    root.destroy()

    info_window = tkinter.Tk()
    info_window.title(f"RBLX Analyzer ({saved_name})")
    icon_path = resource_path("assets\\icon.ico")
    info_window.iconbitmap(icon_path)
    OpenWindow(info_window, 900, 450)
    
    def on_closing():
        global open_graph_windows

        for win in open_graph_windows:
            if win.winfo_exists():
                try:
                    win.destroy()
                except:
                    pass
        open_graph_windows.clear()

        try:
            if info_window.winfo_exists():
                info_window.destroy()
        except:
            pass
        os._exit(0)
    info_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    mainCanvas = tkinter.Canvas(info_window, highlightthickness=0)
    mainCanvas.pack(side="left", fill="both", expand=True)
    infoScrollbar = tkinter.Scrollbar(info_window, orient="vertical", command=mainCanvas.yview)
    infoScrollbar.pack(side="right", fill="y")
    mainCanvas.configure(yscrollcommand=infoScrollbar.set)
    mainFrame = tkinter.Frame(mainCanvas, background="white", width=900, height=450)
    canvasFrame = mainCanvas.create_window((0, 0), window=mainFrame, anchor="nw")

    def on_configure(event):
        mainCanvas.configure(scrollregion=mainCanvas.bbox("all"))
    mainFrame.bind("<Configure>", on_configure)

    def _on_mousewheel(event):
        mainCanvas.yview_scroll(-1 * (event.delta // 120), "units")
    info_window.bind_all("<MouseWheel>", _on_mousewheel)

    def resize_canvas(event):
        mainCanvas.itemconfig(canvasFrame, width=mainCanvas.winfo_width())
    mainCanvas.bind("<Configure>", resize_canvas)

    try:
        with open(f"data\\games\\{saved_name}\\basedata\\readable.json", "r", encoding="utf-8") as json_file:
            basedata = json.load(json_file)
    except Exception as e:
        tkinter.messagebox.showerror("Error", f"Unable to load data, please try again later. Error code: {e}")
        info_window.destroy()
        return

    # ICON
    icon_path = f"data\\games\\{saved_name}\\images\\icon.png"
    print("ICON PATH:", icon_path)
    print("EXISTS:", os.path.exists(icon_path))

    try:
        iconImg = Image.open(icon_path)
        iconImg = iconImg.resize((150, 150))
        tkImg = ImageTk.PhotoImage(iconImg)
        imageLabel = tkinter.Label(mainFrame, image=tkImg)
        imageLabel.image = tkImg
        imageLabel.place(relx=0, rely=0, anchor="nw")
    except Exception as e:
        tkinter.messagebox.showerror("Error", f"Unable to load game icon. Error code: {e}")
    
    #NAME
    nameLabel = ttk.Label(mainFrame, text="NAME:", font=("Arial", 10, "bold"))
    nameLabel.place(relx=0.174, rely=0, anchor="nw")
    def position_name_info():
        mainFrame.update_idletasks()
        x_ne = nameLabel.winfo_x() + nameLabel.winfo_width()
        y_ne = nameLabel.winfo_y()

        nameInfo = ttk.Label(mainFrame, text=f"{basedata['game_name']}", font=("Arial", 10))
        nameInfo.place(x=x_ne, y=y_ne, anchor="nw")

    
    #GAME ID
    idLabel = ttk.Label(mainFrame, text="ID:", font=("Arial", 10, "bold"))
    idLabel.place(relx=0.174, rely=0.045, anchor="nw")
    def position_id_info():
        mainFrame.update_idletasks()
        x_ne = idLabel.winfo_x() + idLabel.winfo_width()
        y_ne = idLabel.winfo_y()

        idInfo = ttk.Label(mainFrame, text=f"Universe ({basedata['game_id']}) / RootPlace ({basedata['root_place_id']})", font=("Arial", 10))
        idInfo.place(x=x_ne, y=y_ne, anchor="nw")

    #CREATOR NAME
    creatorNameLabel = ttk.Label(mainFrame, text="CREATOR NAME:", font=("Arial", 10, "bold"))
    creatorNameLabel.place(relx=0.174, rely=0.085, anchor="nw")
    creatorNameInfo = None
    def position_creatorname_info():
        mainFrame.update_idletasks()
        nonlocal creatorNameInfo
        x_ne = creatorNameLabel.winfo_x() + creatorNameLabel.winfo_width()
        y_ne = creatorNameLabel.winfo_y()

        creatorNameInfo = ttk.Label(mainFrame, text=f"{basedata['creator']['name']}", font=("Arial", 10))
        creatorNameInfo.place(x=x_ne, y=y_ne, anchor="nw")
    def position_verified_badge():
        if basedata['creator']['veryfied'] == True:
            mainFrame.update_idletasks()
            x_ne = creatorNameInfo.winfo_x() + creatorNameInfo.winfo_width()
            y_ne = creatorNameInfo.winfo_y()

            iconImg = Image.open(resource_path("assets\\verified_icon.png"))
            iconImg = iconImg.resize((16, 16))
            tkImg = ImageTk.PhotoImage(iconImg)
            imageLabel = tkinter.Label(mainFrame, image=tkImg)
            imageLabel.image = tkImg
            imageLabel.place(x=x_ne, y=y_ne, anchor="nw")


    #CREATE TYPE
    creatorTypeLabel = ttk.Label(mainFrame, text="CREATOR TYPE:", font=("Arial", 10, "bold"))
    creatorTypeLabel.place(relx=0.174, rely=0.125, anchor="nw")
    def position_creatortype_info():
        mainFrame.update_idletasks()
        x_ne = creatorTypeLabel.winfo_x() + creatorTypeLabel.winfo_width()
        y_ne = creatorTypeLabel.winfo_y()
        
        creatorTypeInfo = ttk.Label(mainFrame, text=f"{basedata['creator']['type']}", font=("Arial", 10))
        creatorTypeInfo.place(x=x_ne, y=y_ne, anchor="nw")

    #CREATE ID
    creatorIdLabel = ttk.Label(mainFrame, text="CREATOR ID:", font=("Arial", 10, "bold"))
    creatorIdLabel.place(relx=0.174, rely=0.165, anchor="nw")
    def position_creatorid_info():
        mainFrame.update_idletasks()
        x_ne = creatorIdLabel.winfo_x() + creatorIdLabel.winfo_width()
        y_ne = creatorIdLabel.winfo_y()
        
        creatorIdInfo = ttk.Label(mainFrame, text=f"{basedata['creator']['id']}", font=("Arial", 10))
        creatorIdInfo.place(x=x_ne, y=y_ne, anchor="nw")

    #GENRE
    gameGenreLabel = ttk.Label(mainFrame, text="GENRE:", font=("Arial", 10, "bold"))
    gameGenreLabel.place(relx=0.174, rely=0.205, anchor="nw")
    def position_genre_info():
        mainFrame.update_idletasks()
        x_ne = gameGenreLabel.winfo_x() + gameGenreLabel.winfo_width()
        y_ne = gameGenreLabel.winfo_y()
        
        gameGenreInfo = ttk.Label(mainFrame, text=f"Main ({basedata['main_genre']}) / Sub ({basedata['sub_genre_1']}, {basedata['sub_genre_2']})", font=("Arial", 10))
        gameGenreInfo.place(x=x_ne, y=y_ne, anchor="nw")
    
    #CREATION DATA
    createdLabel = ttk.Label(mainFrame, text="CREATED:", font=("Arial", 10, "bold"))
    createdLabel.place(relx=0.174, rely=0.245, anchor="nw")
    def position_created_info():
        mainFrame.update_idletasks()
        x_ne = createdLabel.winfo_x() + createdLabel.winfo_width()
        y_ne = createdLabel.winfo_y()
        
        createdInfo = ttk.Label(mainFrame, text=f"{basedata['create_data']}", font=("Arial", 10))
        createdInfo.place(x=x_ne, y=y_ne, anchor="nw")

    #PRICE
    priceLabel = ttk.Label(mainFrame, text="PRICE:", font=("Arial", 10, "bold"))
    priceLabel.place(relx=0.174, rely=0.285, anchor="nw")
    priceInfo = None
    def position_price_info():
        mainFrame.update_idletasks()
        nonlocal priceInfo
        x_ne = priceLabel.winfo_x() + priceLabel.winfo_width()
        y_ne = priceLabel.winfo_y()
        
        priceInfo = ttk.Label(mainFrame, text=f"{basedata['game_price']}", font=("Arial", 10))
        priceInfo.place(x=x_ne, y=y_ne, anchor="nw")
    def position_robux_icon():
        mainFrame.update_idletasks()
        x_ne = priceInfo.winfo_x() + priceInfo.winfo_width()
        y_ne = priceInfo.winfo_y()

        iconImg = Image.open(resource_path("assets\\robux_icon.png"))
        iconImg = iconImg.resize((16, 16))
        tkImg = ImageTk.PhotoImage(iconImg)
        imageLabel = tkinter.Label(mainFrame, image=tkImg)
        imageLabel.image = tkImg
        imageLabel.place(x=x_ne, y=y_ne, anchor="nw")

    #DESCRIPTION
    descriptionTitle = ttk.Label(mainFrame, text="DESCRIPTION:", font=("Arial", 10, "bold"))
    descriptionTitle.place(relx=0.5, rely=0.34, anchor="n")


    descriptionText = tkinter.Text(mainFrame, font=("Arial", 10), wrap="word", highlightthickness=1, bd=0)
    descriptionText.delete("1.0", tkinter.END)
    if not basedata["game_description"] == None:
        descriptionText.insert(tkinter.END, basedata['game_description'])
    else:
        descriptionText.insert(tkinter.END, "")
    descriptionText.config(state=tkinter.DISABLED)
    descriptionText.place(relx=0, rely=0.38, relwidth=0.9995, relheight=0.3)

    #FUNCTIONS
    def show_graph(title, key, color, ylabel):
        analytic_path = f"data/games/{saved_name}/analitic/analitic.json"

        if not os.path.exists(analytic_path):
            print("Файл аналитики не найден.")
            return

        with open(analytic_path, "r", encoding="utf-8") as file:
            analitic_data = json.load(file)

        sorted_items = sorted(analitic_data.items())
        dates = [item[0] for item in sorted_items]
        values = [item[1].get(key, 0) for item in sorted_items]

        chart_window = tkinter.Toplevel()
        chart_window.title(f"RBLX Analyzer ({saved_name}) — {title}")
        icon_path = resource_path("assets\\icon.ico")
        chart_window.iconbitmap(icon_path)
        OpenWindow(chart_window, 1100, 450)
        open_graph_windows.append(chart_window)

        fig, ax = plt.subplots(figsize=(12, 4.5))
        ax.plot(dates, values, marker="o", linestyle="-", color=color)
        ax.set_title(title, fontsize=14)
        ax.set_xlabel("Дата", fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.tick_params(axis='x', rotation=45)
        ax.ticklabel_format(style='plain', axis='y')
        ax.grid(True, linestyle='--', alpha=0.5)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tkinter.BOTH, expand=True)

    def show_active_graph():
        show_graph("Active players", "active", "royalblue", "Players")

    def show_visits_graph():
        show_graph("Visits", "visits", "royalblue", "Visits")

    def show_likes_graph():
        show_graph("Likes", "up_votes", "forestgreen", "Likes")

    def show_dislikes_graph():
        show_graph("Dislikes", "down_votes", "red", "Dislikes")

    def show_favourites_graph():
        show_graph("Favourites", "favourites", "gold", "Added to favourites")

    def show_raiting_graph():
        show_graph("Raiting", "raiting", "gold", "Raiting")

    #BUTTONS
    backButton = ttk.Button(text="Back", command=OpenStartWindow)
    backButton.place(relx=0.01, rely=0.69)

    backButton = ttk.Button(text="Visits", command=show_visits_graph)
    backButton.place(relx=0.1, rely=0.69)

    backButton = ttk.Button(text="Active", command=show_active_graph)
    backButton.place(relx=0.19, rely=0.69)

    backButton = ttk.Button(text="Favourites", command=show_favourites_graph)
    backButton.place(relx=0.28, rely=0.69)
    
    backButton = ttk.Button(text="Likes", command=show_likes_graph)
    backButton.place(relx=0.37, rely=0.69)

    backButton = ttk.Button(text="Dislikes", command=show_dislikes_graph)
    backButton.place(relx=0.46, rely=0.69)
    
    backButton = ttk.Button(text="Raiting", command=show_raiting_graph)
    backButton.place(relx=0.55, rely=0.69)






    def position_all():
        position_name_info()
        position_id_info()
        position_creatorname_info()
        position_verified_badge()
        position_creatortype_info()
        position_creatorid_info()
        position_genre_info()
        position_created_info()
        position_price_info()
        position_robux_icon()

    mainFrame.after(10, position_all)
    info_window.mainloop()
    
    
    
    
    
    
    # def on_frame_configure(event):
    #     mainCanvas.configure(scrollregion=mainCanvas.bbox("all"))

    # def _on_mousewheel(event):
    #     mainCanvas.yview_scroll(-1 * (event.delta // 120), "units")

    # mainFrame.bind("<Configure>", on_frame_configure)
    # info_window.bind_all("<MouseWheel>", _on_mousewheel)



    # # Название игры
    # gameNameLabel = ttk.Label(mainFrame, text=f"{basedata.get('game_name', 'Unknown Game')}")
    # gameNameLabel.place(x=170, y=20)

    # info_window.update_idletasks()
    # mainCanvas.configure(scrollregion=mainCanvas.bbox("all"))

    # info_window.mainloop()



def CheckIdValidation(action, allowed_symbol):
    if action == "1":
        return allowed_symbol.isdigit()
    return True

def CloseIdInputWindow(window, name: str, id):
    allowed_symbols = r"^[A-Za-z0-9\s'-]+$"
    if not re.match(allowed_symbols, name):
        ShowMessage("error", "RBLX ANALYZER", "Invalid save name: This name contains unexpected characters")
        return
    
    name = name.strip()
    if name != "":
        try:
            AddSaved(name, int(id))
        except:
            ShowMessage("error", "RBLX ANALYZER", "Invalid ID: Empty ID")
            return
    else:
        ShowMessage("error", "RBLX ANALYZER", "Invalid save name: Empty name")
        return
    
    window.destroy()

########################################################### BASE DATA ###########################################################
def GetReadableData(primary_data, saved_name, game_id):
    data = primary_data['data'][0]  # Для удобства

    new_data = {
        'game_id': data['id'],
        'root_place_id': data['rootPlaceId'],
        'game_name': data['name'],
        'game_description': data['description'] or None,
        'game_price': data['price'] if data['price'] is not None else 0,
        'main_genre': data.get('genre') or None,
        'sub_genre_1': data.get('genre_l1') or None,
        'sub_genre_2': data.get('genre_l2') or None,
        'creator': {
            'id': data['creator']['id'],
            'name': data['creator']['name'],
            'type': data['creator']['type'],
            'veryfied': data['creator'].get('hasVerifiedBadge', False)
        },
        'create_data': datetime.datetime.strptime(data['created'][:19], "%Y-%m-%dT%H:%M:%S").strftime("%m/%d/%Y %H:%M:%S"),
        'update_data': datetime.datetime.strptime(data['updated'][:19], "%Y-%m-%dT%H:%M:%S").strftime("%m/%d/%Y %H:%M:%S")
    }

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {
        current_time: {
            'visits': data['visits'],
            'active': data['playing'],
            'favourites': data['favoritedCount'],
            'up_votes': data.get('upVotes', 0),
            'down_votes': data.get('downVotes', 0),
            'raiting': data.get('like_dislike_ratio', 0) or 0
        }
    }

    analytic_file_path = os.path.join("data", "games", saved_name, "analitic", "analitic.json")

    if os.path.exists(analytic_file_path):
        try:
            with open(analytic_file_path, "r", encoding="utf-8") as f:
                existing_analytics = json.load(f)
        except Exception:
            existing_analytics = {}
    else:
        existing_analytics = {}

    existing_analytics.update(new_entry)

    with open(analytic_file_path, "w", encoding="utf-8") as f:
        json.dump(existing_analytics, f, indent=4, ensure_ascii=False)

    return [new_data, new_entry]

def GetImages(game_id, saved_name):
    if not os.path.exists(f"data\\games\\{saved_name}\\images"):
        os.makedirs(f"data\\games\\{saved_name}\\images")

    for item in os.listdir(f"data\\games\\{saved_name}\\images"):
        item_path = os.path.join(f"data\\games\\{saved_name}\\images", item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

    icon_url = f"https://thumbnails.roblox.com/v1/games/icons?universeIds={game_id}&size=150x150&format=Png&isCircular=false"
    thumbnails_url = f"https://thumbnails.roblox.com/v1/games/multiget/thumbnails?universeIds={game_id}&countPerUniverse=10&size=480x270&format=png&thumbnailType=Screenshot"

    icon_response = requests.get(icon_url)
    thumbnails_response = requests.get(thumbnails_url)
    
    icon_data = icon_response.json()
    icon_image_url = icon_data['data'][0]['imageUrl']
    icon_img = Image.open(io.BytesIO(requests.get(icon_image_url).content))
    icon_img = icon_img.resize((150, 150), Image.LANCZOS)
    icon_img.save(f"data\\games\\{saved_name}\\images\\icon.png")
    
    thumbnails_data = thumbnails_response.json()
    thumbnails_images_url = [item['imageUrl'] for item in thumbnails_data['data'][0]['thumbnails'] if 'imageUrl' in item][::-1]


    if thumbnails_images_url:
        main_thumbnail_image_url = thumbnails_images_url.pop(0)
        main_thumbnail_image = Image.open(io.BytesIO(requests.get(main_thumbnail_image_url).content))
        main_thumbnail_image = main_thumbnail_image.resize((480, 270), Image.LANCZOS)
        main_thumbnail_image.save(f"data\\games\\{saved_name}\\images\\main-thumbnail.png")

        for id, thumbnail_url in enumerate(thumbnails_images_url):
            thumbnail_image = Image.open(io.BytesIO(requests.get(thumbnail_url).content))
            resized_thumbnail_image = thumbnail_image.resize((480, 270), Image.LANCZOS)
            resized_thumbnail_image.save(f"data\\games\\{saved_name}\\images\\thumbnail{id+1}.png")

def AddData():
    selectedItem = gamesList.focus()
    if not selectedItem:
        return

    values = gamesList.item(selectedItem, "values")
    saved_name = values[1]
    game_id = values[2]

    base_path = f"data\\games\\{saved_name}"
    basedata_path = os.path.join(base_path, "basedata")
    analytic_path = os.path.join(base_path, "analitic")

    os.makedirs(basedata_path, exist_ok=True)
    os.makedirs(analytic_path, exist_ok=True)

    if not CheckRobloxConnection():
        return

    game_url = f"https://games.roblox.com/v1/games?universeIds={game_id}"
    game_response = requests.get(game_url)
    game_data = game_response.json()
    
    raiting_url = f"https://games.roblox.com/v1/games/votes?universeIds={game_id}"
    raiting_response = requests.get(raiting_url)
    raiting_data = raiting_response.json()

    if 'data' in raiting_data and len(raiting_data['data']) > 0:
        rating = raiting_data['data'][0]
        game_data['data'][0]['upVotes'] = rating['upVotes']
        game_data['data'][0]['downVotes'] = rating['downVotes']
        game_data['data'][0]['like_dislike_ratio'] = None
        if rating['upVotes'] + rating['downVotes'] > 0:
            game_data['data'][0]['like_dislike_ratio'] = round((rating['upVotes'] / (rating['upVotes'] + rating['downVotes']) * 100), 2)

    full_path = os.path.join(basedata_path, "full.json")
    with open(full_path, "w", encoding="utf-8") as json_file:
        json.dump(game_data, json_file, indent=4)

    readable_path = os.path.join(basedata_path, "readable.json")
    readable, analytic = GetReadableData(game_data, saved_name, game_id)

    with open(readable_path, "w", encoding="utf-8") as json_file:
        json.dump(readable, json_file, indent=4)

    GetImages(game_id, saved_name)
    OpedInfoWindow(saved_name)





gamesList = None
root = None
def OpenStartWindow():
    global gamesList, root, info_window
    root = tkinter.Tk()
    root.title("RBLX Analyzer")
    icon_path = resource_path("assets\\icon.ico")
    root.iconbitmap(icon_path)
    OpenWindow(root, 900, 450)
    def on_closing():
        try:
            if root.winfo_exists():
                root.destroy()
        except:
            pass
        os._exit(0)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    if info_window != None:
        info_window.destroy()
    mainFrame = ttk.Frame(root)
    gamesList = ttk.Treeview(mainFrame)
    loadGameButton = ttk.Button(mainFrame)
    addGameButton = ttk.Button(mainFrame)
    deleteGameButton = ttk.Button(mainFrame)

    scrollbar = ttk.Scrollbar(mainFrame, orient="vertical", command=gamesList.yview)
    gamesList.config(show="headings", selectmode="browse", columns=("no", "name", "id"), yscrollcommand=scrollbar.set)
    gamesList.heading("no", text="№")
    gamesList.heading("name", text="Name")
    gamesList.heading("id", text="ID")

        # def show_context_menu(event):
        #     selected_item = gamesList.selection()
        #     context_menu = tkinter.Menu(root, tearoff=0)
        #     context_menu.add_command(label="Load", command=lambda: AddData())
        #     context_menu.add_command(label="Add", command=OpedIdInputWindow)
        #     context_menu.add_command(label="Delete", command=lambda: DelFromList())
        #     context_menu.post(event.x_root, event.y_root)
        # gamesList.bind("<Button-3>", show_context_menu)

    loadGameButton.config(text="Load", command=AddData)
    addGameButton.config(text="Add", command=OpedIdInputWindow)
    deleteGameButton.config(text="Delete", command=DelFromList)

    mainFrame.place(relwidth=1, relheight=1)
    gamesList.place(relx=0.005, rely=0.005, relwidth=0.972, relheight=0.925)
    scrollbar.place(relx=0.995, rely=0.005, relheight=0.925, anchor="ne")
    addGameButton.place(rely=0.935, relx=0.005)
    loadGameButton.place(rely=0.935, relx=0.095)
    deleteGameButton.place(rely=0.935, relx=0.185)

    CreateBasePaths()
    UpdateList()

    root.mainloop()

OpenStartWindow()