import toga, os, json, random, asyncio, textwrap, sys, pathlib#, subprocess
import toga.paths
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from toga.platform import current_platform
if os.name == "posix":
    if current_platform == "android":
        from android.content import Intent
        from java import jarray, jbyte
#test de fonctionnement
class QuêteduQI(toga.App):
    async def android_read(self, widget=None) -> bytes:
        fileChose = Intent(Intent.ACTION_GET_CONTENT)
        fileChose.addCategory(Intent.CATEGORY_OPENABLE)
        fileChose.setType("*/*")

        # Assuming `app` is your toga.App object
        results = await self._impl.intent_result(Intent.createChooser(fileChose, "Sélectionner un questionnaire"))  
        data = results['resultData'].getData()
        context = self._impl.native
        stream = context.getContentResolver().openInputStream(data)

        def read_stream(stream):
            block = jarray(jbyte)(1024 * 1024)
            blocks = []
            while True:
                bytes_read = stream.read(block)
                if bytes_read == -1:
                    return b"".join(blocks)
                else:
                    blocks.append(bytes(block)[:bytes_read])
        return read_stream(stream)
    def close_option(self, widget=None):
        if current_platform != "android":
            if self.page == 0:
                self.previous_button.enabled = False
            self.option_window.close()
            self.main_box.refresh()
            self.main_window.show()
        else:
            if self.mode == "simple":
                self.création_question_rafraichir()
            elif self.mode == "QCM":
                self.création_QCM_question()
            elif self.mode == "true/false":
                self.création_truefalse_rafraichir()
            elif self.mode == "multi":
                self.création_multi_checker()
    def startup(self):
        self.quest = []
        self.soluc = []
        self.proprety = []
        self.global_proprety = []
        self.rep = []
        self.reponse = []
        self.version_warn = False
        rang = 0
        self.question_passé = []
        self.page = 0
        self.len_proprety_quiz = 8
        self.len_proprety_QCM = 3
        self.save_state = True
        #version = 2.0
        self.main_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, flex=1))
        self.language = "fr"

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

        self.titre = toga.Label(text="self.titre")
        self.aide = toga.Label(text="self.aide")
        self.desc = toga.Label(text="self.desc")
        self.bouton1 = toga.Button(text="self.bouton1", on_press=self.création_Créer)
        self.bouton3 = toga.Button(text="self.bouton2", on_press=self.null)
        self.bouton2 = toga.Button(text="self.bouton3", on_press=self.null)

        if current_platform == "android":
            path = str(self.app.paths.data).split("/")
            user = path[3]
            self.android_path = f"/storage/emulated/{user}/documents/Quizs/"
            if not(os.path.exists(self.android_path)):
                os.makedirs(self.android_path)

        with open(f"{self.paths.app}/resources/string.json", 'r') as fichier:
            self.strings = json.load(fichier)
        
        self.option_défintion()
        if current_platform != "android":
            self.option_def_menu()
            self.option_main()
        else:
            self.android_startup()
    def error(self, widget, code:int):
        string = self.strings[self.language]["error"]
        if code == 1:
            self.main_window.error_dialog(string[0], string[1])
        elif code == 2:
            self.main_window.error_dialog(string[0], string[2])
    def nav_sup(self, widget):
        if self.mode == "simple":
            del self.quest[self.page], self.soluc[self.page]
            self.création_question_rafraichir()
        elif self.mode == "QCM":
            print(self.soluc)
            a_t = (self.page)*4 + 1
            b_t = (self.page)*4 + 2
            c_t = (self.page)*4 + 3
            d_t = (self.page)*4 + 4
            del self.quest[self.page]
            for _ in range(4):
                self.soluc[a_t]
            self.création_QCM_question()
        elif self.mode == "true/false":
            del self.quest[self.page], self.soluc[self.page]
            self.création_truefalse_rafraichir()
        elif self.mode == "multi":
            print(self.soluc)
            if type(self.soluc[self.page]) == list: del self.rep[self.page]
            del self.quest[self.page], self.soluc[self.page]
            self.création_multi_checker()
    def nav_previous(self, widget):
        self.page -= 1
        if self.mode == "simple":
            self.création_question_rafraichir()
        elif self.mode == "QCM":
            self.création_QCM_question()
        elif self.mode == "true/false":
            self.création_truefalse_rafraichir()
        elif self.mode == "multi":
            self.création_multi_checker()
    def nav_next(self, widget):
        self.page += 1
        if self.mode == "simple":
            self.création_question_rafraichir()
        elif self.mode == "QCM":
            self.création_QCM_question()
        elif self.mode == "true/false":
            self.création_truefalse_rafraichir()
        elif self.mode == "multi":
            self.création_multi_checker()
    def option_défintion(self, widget=None):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        self.main_window.content = self.main_box
        self.titre.style.update(font_family="Calibri light", font_size=30, text_align=CENTER)
        self.aide.style.update(font_family="Calibri light", font_size=20, text_align=CENTER)
        self.desc.style.update(font_family="Calibri light", font_size=12, text_align=CENTER, padding=10)
        self.bouton1.style.update(width=300, padding=(20, 0, 5, 0), font_family="Calibri light", font_size=12)
        self.bouton3.style.update(width=300, padding=(5, 0, 20, 0), font_family="Calibri light", font_size=12)
        self.bouton2.style.update(width=300, font_family="Calibri light", font_size=12)
    def option_taille(self, widget=None):
        self.main_window.info_dialog("Debug",f"Taille de la fenêtre: {self.main_window.size}")
    async def option_skip(self, widget=None):
        self.essaie = 0
        await self.lecture_quiz_check(skip=True)
    def option_def_menu(self, widget=None):
        string = self.strings[self.language]["def_menu"]
        file = toga.Group(string[0])
        action = toga.Group(string[1])
        debug = toga.Group(string[2])
        nav = toga.Group(string[3])
        cmd4 = toga.Command(self.save, string[4], tooltip=string[5], group=file, order=1, shortcut=toga.Key.MOD_1 + 's')
        cmd5 = toga.Command(self.save_to, string[6], tooltip=string[7], group=file, order=2, shortcut=toga.Key.MOD_1 + toga.Key.SHIFT + 's')
        cmd1 = toga.Command(self.création_Créer, string[8], tooltip=string[9], group=action, order=1, shortcut=toga.Key.MOD_1 + 'n')
        cmd2 = toga.Command(self.modifier_load, string[10], tooltip=string[11], group=action, order=2, shortcut=toga.Key.MOD_1 + 'm')
        cmd3 = toga.Command(self.lecture_load, string[12], tooltip=string[13], group=action, order=3, shortcut=toga.Key.MOD_1 + 'o')
        cmd6 = toga.Command(self.option_reset, string[14], tooltip=string[15], group=action, order=4)
        cmd7 = toga.Command(self.option_taille, string[16], tooltip=string[17], group=debug)
        self.next_page = toga.Command(self.nav_next, string[18], tooltip=string[19], group=nav, shortcut=toga.Key.MOD_1 + toga.Key.RIGHT)
        self.prev_page = toga.Command(self.nav_previous, string[20], tooltip=string[21], group=nav, shortcut=toga.Key.MOD_1 + toga.Key.LEFT)
        self.suppr = toga.Command(self.nav_sup, string[22], tooltip=string[23], group=nav, shortcut=toga.Key.DELETE)
        if current_platform == "linux":
            self.suppr.shortcut = toga.Key.MOD_1 + 'e'
        if current_platform == "windows" or current_platform == "linux":self.commands.add(cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7, self.next_page, self.prev_page, self.suppr)
        if current_platform != "windows": self.main_window.toolbar.add(cmd1, cmd2, cmd3, cmd5)
    def option_quit(self, widget=None):
        if current_platform == "android":
            sys.exit()
        else:
            self.main_window.close()
    def option_main(self, widget=None):
        string = self.strings[self.language]["main"]
        self.fichier = ""
        self.change_state_nav(False)
        self.on_exit = self.close_window
        self.titre.text = string[0]
        self.aide.text=string[1]
        if current_platform == "android":
            self.desc.text="\n".join(textwrap.wrap(string[2], width=self.width_windows))
        else: self.desc.text = string[2]
        self.bouton1.on_press, self.bouton1.icon = self.création_Créer, "resources/new.png"
        self.bouton2.on_press, self.bouton2.icon = self.modifier_load, "resources/edit.png"
        self.bouton3.on_press, self.bouton3.icon = self.lecture_load, "resources/read.png"
        self.bouton1.style.update(width=150)
        self.bouton2.style.update(width=150)
        self.bouton3.style.update(width=150)
        self.main_box.add(self.titre, self.aide, self.desc, self.bouton1, self.bouton2, self.bouton3)
    def option_reset(self, widget):
        self.option_défintion()
        self.option_main()
    def option_list(self, widget=None):
        string = self.strings[self.language]["option_list"]
        if current_platform != "android":
            self.main_window.hide()
            self.option_window = toga.Window(title=string[0], on_close=self.close_option)
            self.option_main_box = toga.Box(style=Pack(alignment=CENTER, text_align=CENTER, direction=COLUMN))
            self.option_window.content = self.option_main_box
            option_title = toga.Label(text=string[1], style=Pack(font_family="Calibri Light", font_size=30, text_align=CENTER))
            self.option_main_box.add(option_title)
            if self.proprety[0] == "simple":
                if self.mode == "multi":
                    title_quiz = toga.Button(text=string[2], style=Pack(font_size=12, text_align=CENTER), on_press=lambda widget: self.main_window.info_dialog(string[10], string[11]))
                    self.option_main_box.add(title_quiz)
                self.select_canva = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.checkbox_select = toga.Switch(text="Aide à la réponse", style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER), on_change=self.change_check)
                help_select = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press=self.help_select_window)
                self.inclusive_canva = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.checkbox_inclusive = toga.Switch(text="L'essentiel compte!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
                help_inclusive = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_inclusive_window)
                self.shift_canva = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.checkbox_shift = toga.Switch(text="Pas besoins de majuscule!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
                help_shift = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_shift_window)
                self.show_skip = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.checkbox_show_skip = toga.Switch(text="Je le savais!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
                help_show_skip = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_show_skip_window)
                self.only_skip = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.checkbox_only_skip = toga.Switch(text="Je veux pas savoir!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
                help_only_skip = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_only_skip_window)
                self.congrat = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.checkbox_congrat = toga.Switch(text="Personne n'est parfait!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
                help_congrat = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_congrat)
                self.number_essai = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.label_essai = toga.Label(text=string[3]+str(self.proprety[7])+string[4], style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER))
                help_number_essai = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_number_essai)
                self.number_essai_slider = toga.Slider(style=Pack(width=300), min=1, max=10, tick_count=10, on_release=self.change_check)
                self.checkbox_select.value, self.checkbox_inclusive.value, self.checkbox_shift.value, self.checkbox_show_skip.value, self.checkbox_only_skip.value, self.checkbox_congrat.value, self.number_essai_slider.value = self.proprety[1:]
                self.select_canva.add(self.checkbox_select, help_select)
                self.inclusive_canva.add(self.checkbox_inclusive, help_inclusive)
                self.shift_canva.add(self.checkbox_shift, help_shift)
                self.show_skip.add(self.checkbox_show_skip, help_show_skip)
                self.only_skip.add(self.checkbox_only_skip, help_only_skip)
                self.congrat.add(self.checkbox_congrat, help_congrat)
                self.number_essai.add(self.label_essai, help_number_essai)
                self.checkbox_only_skip.enabled = self.checkbox_show_skip.value
                self.option_main_box.add(self.select_canva, self.inclusive_canva, self.shift_canva, self.show_skip, self.only_skip, self.congrat, self.number_essai, self.number_essai_slider)
            if self.proprety[0] == "QCM":
                self.main_window.hide()
                if self.mode == "QCM" or self.mode == "multi":
                    if self.mode == "multi":
                        title_QCM = toga.Button(text=string[5], style=Pack(font_size=12, text_align=CENTER), on_press=lambda widget: self.main_window.info_dialog(string[10], string[11]))
                        self.option_main_box.add(title_QCM)
                self.mutiple_canva = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
                self.mutiple_switch = toga.Switch(style=Pack(font_family="Calibri light", font_size=12), text="Choix unique", on_change=self.change_check_QCM, value=self.proprety[1])
                self.help_multiple = toga.Button(style=Pack(font_family="Calibri light", font_size=12), text="?", on_press=self.help_multiple_window)
                self.mutiple_canva.add(self.mutiple_switch, self.help_multiple)
                self.number_rep_canva = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
                self.number_rep_switch = toga.Switch(style=Pack(font_family="Calibri light", font_size=12), text="Indiquer le nombre de réponse", on_change=self.change_check_QCM, value=self.proprety[2])
                self.help_number_rep = toga.Button(style=Pack(font_family="Calibri light", font_size=12), text="?", on_press=self.help_number_rep_window)
                self.number_rep_canva.add(self.number_rep_switch, self.help_number_rep)
                self.option_main_box.add(self.mutiple_canva, self.number_rep_canva)
            if self.proprety[0] != "simple" and self.proprety[0] != "QCM":
                title_other = toga.Label(text=string[6], style=Pack(font_size=12, text_align=CENTER))
                self.option_main_box.add(title_other)
            close = toga.Button(text=string[7], style=Pack(font_family="Calibri Light", font_size=12, width=300), on_press=lambda widget: self.close_option())
            self.option_main_box.add(close)
            self.option_window.show()
        else:
            self.option_défintion()
            option_title = toga.Label(text=string[1], style=Pack(font_family="Calibri Light", font_size=30, text_align=CENTER))
            self.main_box.add(option_title)
            if self.proprety[0] == "simple":
                if self.mode == "multi":
                    title_quiz = toga.Button(text=string[12], style=Pack(font_size=12, text_align=CENTER), on_press=lambda widget: self.main_window.info_dialog(string[10], string[11]))
                    self.main_box.add(title_quiz)
                self.select_canva = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.checkbox_select = toga.Switch(text="Aide à la réponse", style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER), on_change=self.change_check)
                help_select = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press=self.help_select_window)
                self.inclusive_canva = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.checkbox_inclusive = toga.Switch(text="L'essentiel compte!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
                help_inclusive = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_inclusive_window)
                self.shift_canva = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.checkbox_shift = toga.Switch(text="Pas besoins de majuscule!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
                help_shift = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_shift_window)
                self.show_skip = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.checkbox_show_skip = toga.Switch(text="Je le savais!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
                help_show_skip = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_show_skip_window)
                self.only_skip = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.checkbox_only_skip = toga.Switch(text="Je veux pas savoir!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
                help_only_skip = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_only_skip_window)
                self.congrat = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.checkbox_congrat = toga.Switch(text="Personne n'est parfait!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
                help_congrat = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_congrat)
                self.number_essai = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
                self.label_essai = toga.Label(text=string[3]+str(self.proprety[7])+string[4], style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER))
                help_number_essai = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_number_essai)
                self.number_essai_slider = toga.Slider(style=Pack(width=300), min=0, max=10, tick_count=11, on_release=self.change_check)
                self.checkbox_select.value, self.checkbox_inclusive.value, self.checkbox_shift.value, self.checkbox_show_skip.value, self.checkbox_only_skip.value, self.checkbox_congrat.value, self.number_essai_slider.value = self.proprety[1:]
                self.select_canva.add(self.checkbox_select, help_select)
                self.inclusive_canva.add(self.checkbox_inclusive, help_inclusive)
                self.shift_canva.add(self.checkbox_shift, help_shift)
                self.show_skip.add(self.checkbox_show_skip, help_show_skip)
                self.only_skip.add(self.checkbox_only_skip, help_only_skip)
                self.congrat.add(self.checkbox_congrat, help_congrat)
                self.number_essai.add(self.label_essai, help_number_essai)
                self.checkbox_only_skip.enabled = self.checkbox_show_skip.value
                self.main_box.add(self.select_canva, self.inclusive_canva, self.shift_canva, self.show_skip, self.only_skip, self.congrat, self.number_essai, self.number_essai_slider)
            if self.proprety[0] == "QCM":
                if self.mode == "QCM" or self.mode == "multi":
                    if self.mode == "multi":
                        title_QCM = toga.Button(text=string[8], style=Pack(font_size=12, text_align=CENTER), on_press=lambda widget: self.main_window.info_dialog(string[10], string[11]))
                        self.main_box.add(title_QCM)
                self.mutiple_canva = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
                self.mutiple_switch = toga.Switch(style=Pack(font_family="Calibri light", font_size=12), text="Choix unique", on_change=self.change_check_QCM, value=self.proprety[1])
                self.help_multiple = toga.Button(style=Pack(font_family="Calibri light", font_size=12), text="?", on_press=self.help_multiple_window)
                self.mutiple_canva.add(self.mutiple_switch, self.help_multiple)
                self.number_rep_canva = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
                self.number_rep_switch = toga.Switch(style=Pack(font_family="Calibri light", font_size=12), text="Indiquer le nombre de réponse", on_change=self.change_check_QCM, value=self.proprety[2])
                self.help_number_rep = toga.Button(style=Pack(font_family="Calibri light", font_size=12), text="?", on_press=self.help_number_rep_window)
                self.number_rep_canva.add(self.number_rep_switch, self.help_number_rep)
                self.main_box.add(self.mutiple_canva, self.number_rep_canva)
            if self.proprety[0] != "simple" and self.proprety[0] != "QCM":
                title_other = toga.Label(text=string[9], style=Pack(font_size=12, text_align=CENTER))
                self.main_box.add(title_other)
            close = toga.Button(text=string[7], style=Pack(font_family="Calibri Light", font_size=12, width=300), on_press=lambda widget: self.close_option())
            self.main_box.add(close)
    def null(self, widget=None, var=None):
        pass
    async def option_aband(self, widget=None):
        string = self.strings[self.language]["aband"]
        message = await self.main_window.question_dialog(string[0], string[1], on_result=self.null)
        if message == True:
            if current_platform == "android":sys.exit()
            else: self.main_window.close()
    def création_Créer(self, widget):
        string = self.strings[self.language]["créer"]
        #self.main_window.info_dialog("Debug",f"Chemin: {self.app.paths.data}")
        self.proprety = []
        self.global_proprety = []
        self.quest = []
        self.soluc = []
        self.fichier = ""
        self.mode = ""
        self.page = 0
        self.change_state_nav(False)
        self.option_défintion()
        self.change_title_main_window(string[0], False)
        try:
            self.option_window.close()
        except (NameError, AttributeError, ValueError):
            pass
        self.titre.text=string[1]
        if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap(string[2], width=self.width_aide))
        else:self.aide.text=string[2]
        if current_platform == "android": self.desc.text= "\n".join(textwrap.wrap(string[3], width=self.width_windows))
        else: self.desc.text = string[3]
        self.bouton1.text=string[4]
        self.bouton1.on_press= self.création_question_rafraichir
        self.bouton2.text=string[5]
        self.bouton2.on_press = self.création_QCM_question
        self.true_false_button = toga.Button(text=string[6], style=Pack(width=300, font_family="Calibri light", font_size=12, padding=(0, 0, 5, 0)), on_press=self.création_truefalse_rafraichir)
        self.multi_button = toga.Button(text=string[7], style=Pack(width=300, font_family="Calibri light", font_size=12), on_press=self.création_multi_checker)
        self.bouton2.style.update(padding_bottom=5)
        self.bouton3.text, self.bouton3.on_press =string[8], self.option_quit
        self.main_box.add(self.titre, self.aide, self.desc, self.bouton1, self.bouton2, self.true_false_button, self.multi_button, self.bouton3)
    def création_multi_checker(self, widget=None):
        string = self.strings[self.language]["multi_checker"]
        self.mode = "multi"
        self.change_state_nav(True)
        if self.global_proprety == []:
            self.global_proprety = ["multi",["simple", False, False, False, False, False, False, 3],["QCM", False, False], ["true/false"]]
        #self.option_def_menu()
        if self.page == len(self.quest):
            self.option_défintion()
            if current_platform == "android": self.titre.text = string[0]
            else:self.titre.text=string[1]
            if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap(string[2], width=self.width_aide))
            else: self.aide.text= string[2]
            if current_platform == "android": self.desc.text = "\n".join(textwrap.wrap(string[3], width=self.width_windows))
            else:self.desc.text = string[3]
            self.type_select = toga.Selection(items=[string[4], string[5], string[6]], style=Pack(width=200, text_align=CENTER))
            if self.page != 0:
                last_question = self.soluc[self.page - 1]
                if type(last_question) == str:
                    self.type_select.value = string[4]
                elif type(last_question) == list:
                    self.type_select.value = string[5]
                elif type(last_question) == bool:
                    self.type_select.value = string[6]
            self.bouton1.text, self.bouton1.on_press = string[7], self.création_multi_selected
            self.bouton2.text, self.bouton2.on_press = string[8], self.save
            self.bouton3.style.update(font_family="Calibri light", font_size=12, text_align=CENTER, width=300)
            self.bouton3.text, self.bouton3.on_press = string[9], self.option_aband
            self.nav = toga.Box(Pack(direction=ROW))
            self.del_button = toga.Button(text=string[10], on_press=self.nav_sup, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
            self.next_button = toga.Button(text=string[11], on_press=self.nav_next ,style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
            self.previous_button = toga.Button(text=string[12], on_press=self.nav_previous, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
            self.nav.add(self.previous_button, self.del_button, self.next_button)
            if self.page == 0: self.previous_button.enabled, self.prev_page.enabled = False, False
            else: self.previous_button.enabled, self.prev_page.enabled = True, True
            self.next_button.enabled, self.del_button.enabled, self.next_page.enabled, self.suppr.enabled = False, False, False, False
            self.main_box.add(self.titre, self.aide, self.desc, self.type_select, self.bouton1, self.bouton2, self.bouton3, self.nav)
            self.bouton1.focus()
        else:
            last_question = self.soluc[self.page]
            if type(last_question) == str:
                self.création_question_rafraichir()
            elif type(last_question) == list:
                self.création_QCM_question()
            elif type(last_question) == bool:
                self.création_truefalse_rafraichir()
        # self.select_canva = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
        # self.checkbox_select = toga.Switch(text="Aide à la réponse", style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER), on_change=self.change_check)
        # help_select = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press=self.help_select_window)
        # self.inclusive_canva = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
        # self.checkbox_inclusive = toga.Switch(text="L'essentiel compte!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
        # help_inclusive = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_inclusive_window)
        # self.shift_canva = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
        # self.checkbox_shift = toga.Switch(text="Pas besoins de majuscule!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
        # help_shift = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_shift_window)
        # self.checkbox_select.value, self.checkbox_inclusive.value, self.checkbox_shift.value = self.proprety[1:4]
        # self.select_canva.add(self.checkbox_select, help_select)
        # self.inclusive_canva.add(self.checkbox_inclusive, help_inclusive)
        # self.shift_canva.add(self.checkbox_shift, help_shift)
        # self.nav.add(
        # self.previous_button,
        # self.del_button,
        # self.next_button
        # )
        #self.entré.focus()
    def création_multi_selected(self, widget=None):
        string = self.strings[self.language]["multi_checker"]
        if self.type_select.value == string[4]:
            self.création_question_rafraichir()
        elif self.type_select.value == string[5]:
            self.création_QCM_question()
        elif self.type_select.value == string[6]:
            self.création_truefalse_rafraichir()
    def création_question_rafraichir(self, widget=None):
        string = self.strings[self.language]["question_refresh"]
        if self.mode != "multi":
            self.mode = "simple"
        elif self.mode == "multi":
            self.proprety = self.global_proprety[1]
        self.phase = "quest"
        self.change_state_nav(True)
        if self.proprety == []:
            self.proprety = ["simple", False, False, False, False, False, False, 3]
        if len(self.proprety) < self.len_proprety_quiz:
            while len(self.proprety) < self.len_proprety_quiz:
                self.proprety.append(False)
            self.main_window.info_dialog(string[0], string[1])
        if self.proprety[7] == False:
            self.proprety[7] = 3
        self.option_défintion()
        #self.option_def_menu()
        if self.page == len(self.quest): 
            if current_platform == "android": self.titre.text = string[2]
            else:self.titre.text=string[3]
        else: 
            if current_platform == "android": self.titre.text = string[4]
            else: self.titre.text=string[5]
        if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap(string[6], width=self.width_aide))
        else:self.aide.text=string[6]
        if current_platform == "android": self.desc.text= "\n".join(textwrap.wrap(string[7], width=self.width_windows))
        else:self.desc.text=string[7]
        self.entré = toga.TextInput(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), on_confirm=self.création_question_soluc)
        if self.page < len(self.quest):
            self.entré.value = self.quest[self.page]
        self.bouton1.text, self.bouton1.on_press = string[8], self.création_question_soluc
        self.bouton2.text, self.bouton2.on_press = string[9], self.save
        self.bouton3.style.update(font_family="Calibri light", font_size=12, text_align=CENTER, width=300)
        self.bouton3.text, self.bouton3.on_press = string[10], self.option_aband
        del self.desc.style.color
        self.nav = toga.Box(Pack(direction=ROW))
        self.del_button = toga.Button(text=string[11], on_press=self.nav_sup, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
        self.next_button = toga.Button(text=string[12], on_press=self.nav_next ,style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
        self.previous_button = toga.Button(text=string[13], on_press=self.nav_previous, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
        self.nav.add(self.previous_button, self.del_button, self.next_button)
        if self.page == 0: self.previous_button.enabled, self.prev_page.enabled = False, False
        else: self.previous_button.enabled, self.prev_page.enabled = True, True
        if self.page == len(self.quest): self.next_button.enabled, self.del_button.enabled, self.next_page.enabled, self.suppr.enabled = False, False, False, False
        else: self.next_button.enabled, self.del_button.enabled, self.next_page.enabled, self.suppr.enabled = True, True, True, True
        self.option_button = toga.Button(text=string[14], style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER, width=300, padding=(20, 0, 0, 0)), on_press=self.option_list)
        self.nav.add(
        self.previous_button,
        self.del_button,
        self.next_button
        )
        self.main_box.add(self.titre, self.aide, self.desc, self.entré, self.bouton1, self.bouton2, self.bouton3, self.nav, self.option_button)
        self.entré.focus()
    def change_check(self, widget):
        string = self.strings[self.language]["change_check"]
        self.proprety = ["simple", self.checkbox_select.value, self.checkbox_inclusive.value, self.checkbox_shift.value, self.checkbox_show_skip.value, self.checkbox_only_skip.value, self.checkbox_congrat.value, int(self.number_essai_slider.value)]
        if self.proprety[4] == False:
            self.checkbox_only_skip.enabled = False
        else:
            self.checkbox_only_skip.enabled = True
        self.label_essai.text = string[0]+str(self.proprety[7])+string[1]
        if current_platform != "android":
            self.option_main_box.refresh()
        else:
            self.main_box.refresh()
        if self.mode == "multi":self.global_proprety[1] = self.proprety
    def change_check_QCM(self, widget):
        self.proprety = ["QCM", self.mutiple_switch.value, self.number_rep_switch.value]
        if self.mode == "multi":self.global_proprety[2] = self.proprety
    def création_question_soluc(self, widget):
        string = self.strings[self.language]["question_soluc"]
        actuel = self.entré.value
        if actuel == "":
            self.main_window.error_dialog(title=string[0], message=string[1])
        else:
            self.main_box.remove(self.nav, self.option_button, self.bouton2)
            self.phase = "soluc"
            self.aide.text=string[2]
            if current_platform == "android": self.desc.text = "\n".join(textwrap.wrap(string[3], width=self.width_windows))
            else:self.desc.text=string[3]
            if self.page == len(self.quest): self.quest = self.quest + [actuel]
            else: self.quest[self.page] = actuel
            self.entré.value, self.entré.on_confirm = "", self.création_question_question
            if self.page < len(self.soluc):
                self.entré.value = self.soluc[self.page]
            self.bouton1.on_press = self.création_question_question
    async def création_question_question(self, widget):
        string = self.strings[self.language]["question_question"]
        self.phase = "quest"
        actuel = self.entré.value
        if actuel == "\\":
            demande = await self.main_window.confirm_dialog(title=string[0],message=string[1], on_result=self.null)
            if demande == True:
                del self.quest[self.page]
                try:
                    del self.soluc[self.page]
                except IndexError:
                    print("soluc[page] non supprimé car l'index est introuvable")
                self.création_question_rafraichir()
        elif actuel == "":
            self.main_window.error_dialog(title=string[2], message=string[3])
        elif actuel != "":
            self.phase = "quest"
            if self.page == len(self.soluc): 
                self.soluc = self.soluc + [actuel]
                if self.mode == "multi":
                    self.rep.append("")
                self.page += 1
            else: 
                self.soluc[self.page] = actuel
                if self.mode == "multi":
                    self.rep[self.page] = ""
            if self.fichier == "":
                self.change_title_main_window(string[4], False)
            else:
                self.change_title_main_window(str(self.fichier).split("\\")[-1][:-5], False)
            if self.mode == "multi":
                self.création_multi_checker()
            else:
                self.création_question_rafraichir()
            # entré.delete("0","end")
            # bouton1.config(text = "Valider question", on_press=création.question.réponse)
    async def save(self, widget):
        string = self.strings[self.language]["save"]
        #actuel = self.entré.value
        #warn = await self.main_window.question_dialog(title="Sauvegarder?", message="Voulez sauvegarder maintenant?", on_result=self.null)
        #save = False
        if self.quest != [] and self.soluc != []:
            if current_platform == "android":
                self.titre.text = string[0]
                self.aide.text = string[1]
                self.desc.text = "\n".join(textwrap.wrap(string[2], width=self.width_windows))
                self.entré.value = string[3]
                if type(self.soluc[self.page]) == bool:
                    self.main_box.remove(self.truefalse_rep)
                self.bouton1.on_press, self.bouton1.text = self.file_selected, string[0]
                self.main_window.info_dialog(string[4], string[5])
                self.main_box.remove(self.bouton2, self.bouton3, self.nav, self.option_button)
            else:
                if self.fichier == "":
                    self.fichier = await self.main_window.save_file_dialog(title=string[6], suggested_filename=string[7] ,file_types=["json"], on_result=self.file_selected)
                else:
                    await self.file_selected()
        else:
            self.main_window.error_dialog(string[8], string[9])
    async def file_selected(self, widget=None, dontknown=None):
        string = self.strings[self.language]["file_selected"]
        if current_platform == "android":
            if dontknown == "android":
                pass
            elif self.entré.value != "":
                self.fichier = f"{self.android_path}{self.entré.value}.json"
            else:
                self.fichier = False
            if str(self.fichier) == f"{self.android_path}Choisir un questionnaire.json":
                self.fichier = False
        if (self.fichier != None) and self.fichier != False:
            dico = {}
            if self.global_proprety == []:
                dico["proprety"] = self.proprety
                dico["quest"] = self.quest
                dico["soluc"] = self.soluc
                if self.proprety[0] == "QCM":
                    dico["rep"] = self.rep
            else:
                dico["proprety"] = self.global_proprety
                dico["quest"] = self.quest
                dico["soluc"] = self.soluc
                dico["rep"] = self.rep
            try:
                with open (str(self.fichier),'w') as fichie:
                    fichie.write(json.dumps(dico, indent=4))
            except PermissionError:
                if current_platform == "android":
                    self.fichier = self.fichier[:-5]+"_temp.json"
                    try:
                        with open (str(self.fichier),'w') as fichie:
                            fichie.write(json.dumps(dico, indent=4))
                        self.main_window.error_dialog(string[0], string[1])
                    except PermissionError:
                        self.main_window.error_dialog(string[2], string[3])
                else:
                    self.main_window.error_dialog(title=string[4], message=string[5])
            else:
                await self.main_window.info_dialog(title=string[6], message=string[7])
                # if type(self.fichier) == str:
                #     print(type(self.fichier))
                #     print("Méthode par défault utilisée")
                #     filename = str(self.fichier).split("\\")[-1]
                # else:
                #     filename = self.fichier.name
                self.change_title_main_window(str(self.fichier).split("\\")[-1][:-5], True)
                if current_platform == "android":
                    await self.option_aband()
        else:
            self.main_window.error_dialog(title=string[8], message=string[9])
        if self.mode == "simple": self.création_question_rafraichir()
        elif self.mode == "QCM": self.création_QCM_question()
        elif self.mode == "true/false": self.création_truefalse_rafraichir()
        elif self.mode == "multi": self.création_multi_checker()
    async def save_to(self, widget):
        #actuel = self.entré.value
        #warn = await self.main_window.question_dialog(title="Sauvegarder?", message="Voulez sauvegarder maintenant?", on_result=self.null)
        #save = False
        if self.quest != [] and self.soluc != []:
            if current_platform == "android":
                self.titre.text = "Sauvegarder"
                self.aide.text = "Choisir un nom\nde fichier"
                self.desc.text = "\n".join(textwrap.wrap("Veuillez entrer un nom de questionnaire puis appuyer sur \"Sauvegarder\" pour lancer la sauvegarde\nPour modifier un questionnaire précedemment crée, entrer à nouveau son nom, puis validé!", width=self.width_windows))
                self.entré
                self.bouton1.on_press = self.file_selected
                self.main_box.remove(self.bouton2, self.bouton3, self.nav, self.option_text, self.inclusive_canva, self.select_canva, self.shift_canva)
                self.main_window.info_dialog("Restrictions Android", "Dû aux restrictions Android, il n'est pas possible de choisir l'emplacement de sauvegarde du fichier. Les quizs sont sauvegardé dans \"Espace partagé/documents/Quizs/\"")
            else:
                self.fichier = await self.main_window.save_file_dialog(title="Sauvegarder le questionnaire", suggested_filename="Sans nom.json" ,file_types=["json"], on_result=self.file_selected)
        else:
            self.main_window.error_dialog("Impossible de sauvegarder", "Votre questionnaire est incomplet, assurez vous d'en avoir déjà importé ou crée un") 
    def help_select_window(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="Si vous activez cette option, lors du test pour ce questionnaire, l'utilisateur pourra accéder à une liste de toute les réponses disponible de ce questionnaire et pourra sélectionner celle qui lui semble le mieux!")
    def help_inclusive_window(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="Si vous activez cette option, lors du test pour ce questionnaire, si la moitié ou plus (qu'importe l'ordre) des mots de la réponse, correspondent à la réponse de la question, la réponse donnée en sera validée\nASTUCE (Version >= 2.2): Si certains mots ou partie de phrase vous semblent nécessaire d'être mentionné, rédigé ces parties entre **\nUtile si le questionnaire contient beaucoup de réponses avec des phrases comprennant plusieurs mots")
    def help_shift_window(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="Si vous activez cette option, lors du test pour ce questionnaire, une réponse pourra être validée, même si l'utilisateur ne respecte pas les majuscules (et minuscules)\nUtile si les majuscules de vos réponses ne sont pas importantes!")
    def help_multiple_window(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="Si cette option est activée, l'utilisateur devra choisir une réponse parmi les 4 disponibles, si il choisit une des bonnes réponses, la question en sera validée.\nLorsque l'option est désactivée, l'utilisateur devra sélectionner toutes les réponses qu'il juge correct, ATTENTION: Il devra valider TOUTES les bonnes réponses")
    def help_number_rep_window(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="Si cette option est activée, l'utilisateur sera tenu informé du nombre de réponses possibles")
    def help_show_skip_window(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="Si cette option est activée, lorsque l'utilisateur passera une question, la bonne réponse ne lui sera pas dévoillée")
    def help_only_skip_window(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="(Cette option ne s'applique que si l'option \"Je le savais!\" est activée) Si cette option est activée, l'utilisateur ne verra également pas la réponse si il a utilisé tout ces essais, en plus de ne pas pouvoir la connaître en passant la question!")
    def help_congrat(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="Si cette option est activée, le questionnaire sera considéré comme étant un \"sans-faute\" même si l'utilisateur fait des fautes. Seuls passer la question ou être à court d'essais, annule la mention \"sans-faute\"")
    def help_number_essai(self, widget):
        self.main_window.info_dialog("Aide de l'option", "Par défault sur 3, ce paramètre permet de modifier le nombre d'essais par question autorisé à l'utilisateur (réglable de 0 à 10 essais)")
    def création_QCM_question(self, widget=None):
        string = self.strings[self.language]["QCM_question"]
        self.phase = "quest"
        if self.mode != "multi":
            self.mode = "QCM"
        elif self.mode == "multi":
            self.proprety = self.global_proprety[2]
        self.change_state_nav(True)
        self.option_défintion()
        if self.proprety == []:
            self.proprety = [self.mode, False, False]
        if len(self.proprety) < self.len_proprety_QCM:
            while len(self.proprety) < self.len_proprety_QCM:
                self.proprety.append(False)
            self.main_window.info_dialog(string[0], string[1])
        if self.page == len(self.quest): 
            self.titre.text=string[2]
            if current_platform == "android": self.desc.text = "\n".join(textwrap.wrap(string[3], width=self.width_aide))
            else:self.aide.text = string[3]
        else: self.titre.text=string[4]
        if current_platform == "android": self.desc.text = "\n".join(textwrap.wrap(string[5], width=self.width_windows))
        else:self.desc.text=string[5]
        self.entré = toga.TextInput(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), on_confirm=self.création_QCM_soluc)
        if self.page < len(self.quest):
            self.entré.value = self.quest[self.page]
        self.bouton1.text, self.bouton1.on_press = string[6], self.création_QCM_soluc
        self.bouton2.text, self.bouton2.on_press = string[7], self.save
        self.bouton3.text, self.bouton3.on_press = string[8], self.option_aband
        self.nav = toga.Box(style=Pack(direction = ROW))
        next_button = toga.Button(text=string[9], on_press=self.nav_next, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
        previous_button = toga.Button(text=string[10], on_press=self.nav_previous, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
        del_button = toga.Button(text=string[11], on_press=self.nav_sup, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
        self.option_button = toga.Button(text=string[12], style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER, width=300, padding=(20, 0, 0, 0)), on_press=self.option_list)
        if self.page == 0: previous_button.enabled = False
        else: previous_button.enabled = True
        if self.page == len(self.quest): next_button.enabled, del_button.enabled = False, False
        else: next_button.enabled, del_button.enabled = True, True
        self.nav.add(previous_button, del_button, next_button)
        self.main_box.add(self.titre, self.aide, self.desc, self.entré, self.bouton1, self.bouton2, self.bouton3, self.nav, self.option_button)
        self.entré.focus()
    def création_QCM_soluc(self, widget):
        string = self.strings[self.language]["QCM_soluc"]
        if self.entré.value == "":
            self.main_window.error_dialog(title=string[0], message=string[1])
        else:
            self.phase = "soluc"
            self.question = self.entré.value
            self.option_défintion()
            self.titre.text = string[2]
            if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap(string[3], width=self.width_aide))
            else:self.aide.text = string[4]
            if current_platform == "android": self.desc.text = "\n".join(textwrap.wrap(string[5], width=self.width_windows))
            else:self.desc.text = string[5]
            self.a_box = toga.Box(style=Pack(direction = ROW))
            self.b_box = toga.Box(style=Pack(direction = ROW))
            self.c_box = toga.Box(style=Pack(direction = ROW))
            self.d_box = toga.Box(style=Pack(direction = ROW))
            self.A_s = toga.Switch(style=Pack(font_size=12), text="")
            self.B_s = toga.Switch(style=Pack(font_size=12), text="")
            self.C_s = toga.Switch(style=Pack(font_size=12), text="")
            self.D_s = toga.Switch(style=Pack(font_size=12), text="")
            self.A_e = toga.TextInput(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), on_confirm=self.création_QCM_at_save)
            self.B_e = toga.TextInput(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), on_confirm=self.création_QCM_at_save)
            self.C_e = toga.TextInput(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), on_confirm=self.création_QCM_at_save)
            self.D_e = toga.TextInput(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), on_confirm=self.création_QCM_at_save)
            self.a_box.add(self.A_e, self.A_s)
            self.b_box.add(self.B_e, self.B_s)
            self.c_box.add(self.C_e, self.C_s)
            self.d_box.add(self.D_e, self.D_s)
            a_t = (self.page)*4 + 0
            b_t = (self.page)*4 + 1
            c_t = (self.page)*4 + 2
            d_t = (self.page)*4 + 3
            if self.page < len(self.quest):
                if self.mode == "QCM":
                    self.A_e.value = self.soluc[a_t]
                    self.B_e.value = self.soluc[b_t]
                    self.C_e.value = self.soluc[c_t]
                    self.D_e.value = self.soluc[d_t]
                else:
                    self.A_e.value = self.soluc[self.page][0]
                    self.B_e.value = self.soluc[self.page][1]
                    self.C_e.value = self.soluc[self.page][2]
                    self.D_e.value = self.soluc[self.page][3]
                self.A_s.value = self.get_rep("A", self.rep[self.page])
                self.B_s.value = self.get_rep("B", self.rep[self.page])
                self.C_s.value = self.get_rep("C", self.rep[self.page])
                self.D_s.value = self.get_rep("D", self.rep[self.page])
            self.bouton1.text, self.bouton1.on_press = string[6], self.création_QCM_at_save
            #bouton2.config(text = "Terminer", command=option.null)
            self.bouton3.text, self.bouton3.on_press = string[7], self.option_aband
            self.main_box.add(self.titre, self.aide, self.a_box, self.b_box, self.c_box, self.d_box, self.desc, self.bouton1, self.bouton3)
            self.A_e.focus()
    def création_QCM_at_save(self, widget):
        string = self.strings[self.language]["QCM_at_save"]
        if (self.A_s.value == False and self.B_s.value == False and self.C_s.value == False and self.D_s.value == False) or (self.A_e.value == "" or self.B_e.value == "" or self.C_e.value == "" or self.D_e.value == ""):
            self.main_window.error_dialog(string[0], string[1])
        else:
            rep = ""
            if self.A_s.value == True:
                rep += "A"
            if self.B_s.value == True:
                rep += "B"
            if self.C_s.value == True:
                rep += "C"
            if self.D_s.value == True:
                rep += "D"
            if len(rep) >= 2 and self.version_warn == False:
                self.main_window.info_dialog(string[2], string[3])
                self.version_warn = True
            if self.fichier == "":
                self.change_title_main_window(string[4], False)
            else:
                self.change_title_main_window(str(self.fichier).split("\\")[-1][:-5], False)
            if len(self.quest) == self.page:
                if self.mode == "QCM":
                    for x in self.A_e.value, self.B_e.value, self.C_e.value, self.D_e.value:
                        self.soluc.append(x)
                else:
                    self.soluc.append([self.A_e.value, self.B_e.value, self.C_e.value, self.D_e.value])
                self.quest.append(self.question)
                self.rep.append(rep)
                self.page += 1
                if self.mode == "multi":
                    self.création_multi_checker()
                else:self.création_QCM_question()
            else:
                self.quest[self.page] = self.question
                self.rep[self.page] = (rep)
                a_t = (self.page)*4 + 0
                b_t = (self.page)*4 + 1
                c_t = (self.page)*4 + 2
                d_t = (self.page)*4 + 3
                if self.mode == "QCM":
                    self.soluc[a_t] = self.A_e.value
                    self.soluc[b_t] = self.B_e.value
                    self.soluc[c_t] = self.C_e.value
                    self.soluc[d_t] = self.D_e.value
                    self.création_QCM_question()
                else:
                    self.soluc[self.page][0] = self.A_e.value
                    self.soluc[self.page][1] = self.B_e.value
                    self.soluc[self.page][2] = self.C_e.value
                    self.soluc[self.page][3] = self.D_e.value
                    self.création_multi_checker()
    def création_truefalse_rafraichir(self, widget=None):
        string = self.strings[self.language]["truefalse_refresh"]
        if self.mode != "multi":
            self.mode = "true/false"
        elif self.mode == "multi":
            self.proprety = self.global_proprety[3]
        self.phase = "quest"
        self.change_state_nav(True)
        if self.proprety == []:
            self.proprety = ["true/false"]
        self.option_défintion()
        #self.option_def_menu()
        if self.page == len(self.quest): 
            if current_platform == "android": self.titre.text = string[0]
            else:self.titre.text=string[1]
        else: 
            if current_platform == "android": self.titre.text = string[2]
            else: self.titre.text=string[3]
        if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap(string[4], width=self.width_aide))
        else:self.aide.text=string[4]
        if current_platform == "android": self.desc.text= "\n".join(textwrap.wrap(string[5], width=self.width_windows))
        else:self.desc.text=string[5]
        self.entré = toga.TextInput(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), on_confirm=self.création_truefalse_save)
        self.bouton1.text, self.bouton1.on_press = string[6], self.création_truefalse_save
        self.bouton1.style.update(font_family="Calibri light", font_size=12)
        self.bouton2.text, self.bouton2.on_press = string[7], self.save
        self.bouton2.style.update(font_family="Calibri light", font_size=12)
        self.bouton3 = toga.Button(text=string[8], on_press=self.option_aband, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER, width=300, padding=(5, 0, 20, 0)))
        self.nav = toga.Box(Pack(direction=ROW))
        self.del_button = toga.Button(text=string[9], on_press=self.nav_sup, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
        self.next_button = toga.Button(text=string[10], on_press=self.nav_next ,style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
        self.previous_button = toga.Button(text=string[11], on_press=self.nav_previous, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
        self.truefalse_box = toga.Box(style=Pack(alignment=CENTER, direction=ROW))
        self.truefalse_rep = toga.Switch(style=Pack(font_size=12, font_family="Calibri light", text_align=CENTER, padding_top=10), text="Activer si vrai")
        self.option_button = toga.Button(text=string[12], style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER, width=300, padding=(20, 0, 0, 0)), on_press=self.option_list)
        if self.page < len(self.quest):
            self.truefalse_rep.value = self.soluc[self.page]
            self.entré.value = self.quest[self.page]
        self.truefalse_rep.on_change = self.création_truefalse_save
        self.truefalse_box.add(self.truefalse_rep)
        self.nav.add(self.previous_button, self.del_button, self.next_button)
        if self.page == 0: self.previous_button.enabled, self.prev_page.enabled = False, False
        else: self.previous_button.enabled, self.prev_page.enabled = True, True
        if self.page == len(self.quest): self.next_button.enabled, self.del_button.enabled, self.next_page.enabled, self.suppr.enabled = False, False, False, False
        else: self.next_button.enabled, self.del_button.enabled, self.next_page.enabled, self.suppr.enabled = True, True, True, True
        self.main_box.add(self.titre, self.aide, self.desc, self.entré, self.truefalse_box, self.bouton1, self.bouton2, self.bouton3, self.nav, self.option_button)
        self.entré.focus()
    def création_truefalse_save(self, widget=None):
        string = self.strings[self.language]["truefalse_save"]
        actuel = self.truefalse_rep.value
        question = self.entré.value
        if question != "":
            if self.fichier == "":
                self.change_title_main_window(string[0], False)
            else:
                self.change_title_main_window(str(self.fichier).split("\\")[-1][:-5], False)
            self.phase = "quest"
            if self.page == len(self.soluc):
                self.quest += [question]
                self.soluc = self.soluc + [actuel]
                self.rep.append("")
                self.page += 1
            else: 
                self.quest[self.page] = question
                self.soluc[self.page] = actuel
                self.rep[self.page] = ""
            if self.mode == "multi":
                self.création_multi_checker()
            else:
                self.création_truefalse_rafraichir()
        else:
            self.main_window.error_dialog(string[1], string[2])
    async def modifier_load(self, widget):
        string = self.strings[self.language]["load"]
        self.page = 0
        if current_platform == "android":
            suite = True
            content = await self.android_read()
            #self.main_window.info_dialog("Debug", "Content: "+str(content)+"\nContent décodé: "+content.decode("utf_8"))
            try:
                dico = json.loads(str(content.decode("utf-8")))
            except json.JSONDecodeError:
                self.main_window.error_dialog(title=string[0], message=string[1])
                suite = False
            try:
                self.proprety = dico["proprety"]
                self.quest = dico["quest"]
                self.soluc = dico["soluc"]
                if self.proprety[0] == "QCM" or self.proprety[0] == "multi": self.rep = dico["rep"]
            except (KeyError, IndexError):
                self.main_window.error_dialog(title=string[2], message=string[3])
                suite = False
            if suite == True:
                self.global_proprety = []
                self.mode = self.proprety[0]
                self.change_title_main_window(str(self.fichier).split("/")[-1][:-5], True)
                if self.proprety[0] == "simple":
                    self.création_question_rafraichir()
                elif self.proprety[0] == "QCM":
                    self.création_QCM_question()
                elif self.proprety[0] == "true/false":
                    self.création_truefalse_rafraichir()
                elif self.proprety[0] == "multi":
                    self.global_proprety = self.proprety
                    self.création_multi_checker()
            #self.main_window.info_dialog("Debug", f"Résultat de content: {content}")
            #if reponse.returncode == 0:
            #    self.main_window.info_dialog("Debug", f"Contenu de la fonction ls:{reponse.stdout}")
            #else:
            #     self.main_window.error_dialog("Debug", f"La commande ls a retournéune erreur: {reponse.stderr}")
            #self.main_window.info_dialog("Debug",f"Fichiers: {glob.glob("{self.android_path}*.json")}\nChemin d'origine: {self.android_path}")
            # quizs = []
            # for x in fichier:
            #     if x[-5:].lower() == ".json":
            #         quizs.append(x[:-5])
            # self.file_choose = toga.Selection(items=["Choisir un questionnaire"]+quizs, style=Pack(width=200))
            # choose_box.add(self.file_choose, toga.Button("Importer", style=Pack(width=150), on_press=self.modifier_load_selected))
            #self.main_box.add(self.titre, self.aide, self.desc, self.bouton3, choose_box)
        else:
            self.fichier = await self.main_window.open_file_dialog(title=string[4], file_types=["json"], on_result=self.modifier_load_selected)
    def modifier_load_selected(self, widget=None, dontknown=None):
        #A réunir
        suite = True
        self.fichier = dontknown
        if (self.fichier != None) and self.fichier != False:
            try:
                with open (str(self.fichier), 'r') as fichie:
                    dico = json.load(fichie)
            except json.JSONDecodeError:
                self.main_window.error_dialog(title="Erreur JSON", message="Impossible d'ouvrir ce questionnaire car le fichier JSON est corrompu!")
                suite = False
            try:
                self.proprety = dico["proprety"]
                self.quest = dico["quest"]
                self.soluc = dico["soluc"]
                if self.proprety[0] == "QCM" or self.proprety[0] == "multi": self.rep = dico["rep"]
            except (KeyError, IndexError):
                self.main_window.error_dialog(title="Erreur de format", message="Certaines données présente dans le fichier sont incorrectes! Impossible d'ouvrir le questionnaire!")
                suite = False
            if suite == True:
                try:
                    self.option_window.close()
                except (NameError, AttributeError, ValueError):
                    pass
                self.global_proprety = []
                self.mode = self.proprety[0]
                self.change_title_main_window(str(self.fichier).split("\\")[-1][:-5], True)
                if self.proprety[0] == "simple":
                    self.création_question_rafraichir()
                elif self.proprety[0] == "QCM":
                    self.création_QCM_question()
                elif self.proprety[0] == "true/false":
                    self.création_truefalse_rafraichir()
                elif self.proprety[0] == "multi":
                    self.global_proprety = self.proprety
                    self.création_multi_checker()
        else:
            self.main_window.error_dialog(title="Aucun fichier choisie", message="Vous n'avez pas choisie de fichier lorsque cela l'a été demandé!")
    async def lecture_load(self, widget):
        string = self.strings[self.language]["load"]
        self.page = 0
        if current_platform == "android":
            suite = True
            content = await self.android_read()
            #self.main_window.info_dialog("Debug", "Content: "+str(content)+"\nContent décodé: "+content.decode("utf_8"))
            try:
                dico = json.loads(str(content.decode("utf-8")))
            except json.JSONDecodeError:
                self.main_window.error_dialog(title=string[0], message=string[1])
                suite = False
            try:
                self.proprety = dico["proprety"]
                self.quest = dico["quest"]
                self.soluc = dico["soluc"]
                if self.proprety[0] == "QCM" or self.proprety[0] == "multi": self.rep = dico["rep"]
            except (KeyError, IndexError):
                self.main_window.error_dialog(title=string[2], message=string[3])
                suite = False
                self.question_passé = []
            if suite == True:
                self.global_proprety = []
                self.change_state_nav(False)
                self.clear = True
                self.question_passé = []
                self.change_title_main_window(str(self.fichier).split("\\")[-1][:-5], True)
                if self.proprety[0] == "simple":
                    await self.lecture_quiz_test()
                elif self.proprety[0] == "QCM":
                    await self.lecture_QCM_test()
                elif self.proprety[0] == "true/false":
                    await self.lecture_truefalse_test()
                elif self.proprety[0] == "multi":
                    self.global_proprety = self.proprety
                    await self.lecture_multi_check()
        else:
            self.fichier = await self.main_window.open_file_dialog(title=string[4], file_types=["json"], on_result=self.lecture_load_selected)
    async def lecture_load_selected(self, widget=None, dontknown=None):
        #A réunir
        suite = True
        self.fichier = dontknown
        if (self.fichier != None) and self.fichier != False:
            try:
                with open (str(self.fichier), 'r') as fichie:
                    dico = json.load(fichie)
            except json.JSONDecodeError:
                self.main_window.error_dialog(title="Erreur JSON", message="Impossible d'ouvrir ce questionnaire car le fichier JSON est corrompu!")
                suite = False
            try:
                self.proprety = dico["proprety"]
                self.quest = dico["quest"]
                self.soluc = dico["soluc"]
                if self.proprety[0] == "QCM" or self.proprety[0] == "multi": self.rep = dico["rep"]
            except (KeyError, IndexError):
                self.main_window.error_dialog(title="Erreur de format", message="Certaines données présente dans le fichier sont incorrectes! Impossible d'ouvrir le questionnaire!")
                suite = False
            if suite == True:
                try:
                    self.option_window.close()
                except (NameError, AttributeError, ValueError):
                    pass
                self.global_proprety = []
                self.change_state_nav(False)
                self.clear = True
                self.question_passé = []
                self.change_title_main_window(str(self.fichier).split("\\")[-1][:-5], True)
                if self.proprety[0] == "simple":
                    await self.lecture_quiz_test()
                elif self.proprety[0] == "QCM":
                    await self.lecture_QCM_test()
                elif self.proprety[0] == "true/false":
                    await self.lecture_truefalse_test()
                elif self.proprety[0] == "multi":
                    self.global_proprety = self.proprety
                    await self.lecture_multi_check()
        else:
            self.main_window.error_dialog(title="Aucun fichier choisie", message="Vous n'avez pas choisie de fichier lorsque cela l'a été demandé!")
    async def lecture_quiz_test(self, widget=None):
        string = self.strings[self.language]["quiz_test"]
        if self.global_proprety == []:
            nb_quest = len(self.quest) - 1
            self.question = random.randint(0, nb_quest)
            if len(self.question_passé) == nb_quest + 1:
                if self.clear == True:
                    await self.main_window.info_dialog(title=string[0], message=string[1], on_result=self.null)
                warn = await self.main_window.question_dialog(title=string[0], message=string[2], on_result=self.null)
                if warn == True:
                    if current_platform == "android": sys.exit()
                    else: self.main_window.close()
                else:
                    self.question = random.randint(0, nb_quest)
                    self.question_passé = []
                    self.clear = True
            else:
                while self.question in self.question_passé:
                    self.question = random.randint(0, nb_quest)
        else:
            self.proprety = self.global_proprety[1]
        if len(self.proprety) < self.len_proprety_quiz:
            if await self.main_window.confirm_dialog(string[3], string[4], on_result=self.null):
                self.page = 0
                self.mode = "simple"
                if self.global_proprety == []:
                    await self.création_question_rafraichir()
                else:
                    await self.création_multi_checker()
            else:
                await self.main_window.error_dialog(string[5], string[6], on_result=self.null)
                self.option_quit()
        self.option_défintion()
        if current_platform == "android": self.titre.text = string[7]
        else:self.titre.text=string[8]
        if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap(self.quest[self.question], width=self.width_aide))
        else:self.aide.text=self.quest[self.question]
        if current_platform == "android" : self.desc.text = "\n".join(textwrap.wrap(string[9], width=self.width_windows))
        else:self.desc.text = string[9]
        if (self.proprety[2]) or (self.proprety[3]) or (self.proprety[4]) or (self.proprety[6]):
            text = string[10]
            if self.proprety[2]:
                text += string[11]
            if self.proprety[3]:
                text += string[12]
            if self.proprety[4]:
                if self.proprety[5]:
                    text += string[13]+string[14]
                else:
                    text += string[13]
            if self.proprety[6]:
                text +=string[15]
            if current_platform == "android": self.desc.text = "\n".join(textwrap.wrap(text, width=self.width_windows))
            else:self.desc.text=text
            self.desc.style.update(color="#FF0000")
        else:
            del self.desc.style.color
        self.entré = toga.TextInput(style=Pack(font_family = "Calibri light", font_size = 12, width=300), on_confirm=self.lecture_quiz_check)
        self.bouton1.text, self.bouton1.on_press = string[16], self.lecture_quiz_check
        self.passer = toga.Button(text="Passer",on_press=self.option_skip, style=Pack(width=300, font_family="Calibri light", font_size=12, padding=(0, 0, 5, 0)))
        self.bouton2.text, self.bouton2.on_press = string[17], self.option_aband
        self.help_canva = toga.Box(style=Pack(direction = ROW))
        self.main_box.add(self.titre, self.aide, self.desc, self.entré, self.bouton1, self.passer, self.bouton2)
        self.essaie = self.proprety[7] - 1
        if self.global_proprety == []:
            soluc_list = self.soluc
        else:
            soluc_list = []
            for x in self.soluc:
                if type(x) == str:
                    soluc_list.append(x)
        if self.proprety[1]:
            final_help = []
            lst_append = []
            for x in soluc_list:
                random_index = random.randint(0, len(soluc_list)-1)
                while random_index in lst_append:
                    random_index = random.randint(0, len(soluc_list)-1)
                lst_append.append(random_index)
                final_help.append(soluc_list[random_index])
            self.option_menu = toga.Selection(style=Pack(width=200), items=[string[18]]+final_help, value="Choisir une réponse")
            insert_button = toga.Button(text=string[19], on_press= lambda widget: setattr(self.entré, 'value', self.option_menu.value))
            self.help_canva.add(self.option_menu, insert_button)
            self.main_box.add(self.help_canva)
        else:
            cannot = toga.Label(text=string[20], style=Pack(font_family="Calibri light", font_size=12, text_align = CENTER))
            if current_platform == "android": cannot.text = "\n".join(textwrap.wrap(string[20], width=self.width_windows))
            self.main_box.add(cannot)
        self.entré.focus()
    async def lecture_quiz_check(self, widget=None, skip=None):
        string = self.strings[self.language]["quiz_check"]
        don = self.entré.value
        resp = self.soluc[self.question].replace("*","")
        if don != resp:
            legit = False
        else:
            legit = True
        if self.proprety[3]:
            don = don.lower()
            resp = self.soluc[self.question].lower()
        if self.proprety[2]:
            word_resp = don.split(" ")
            treated = resp.split(" ")
            objectif = len(treated)//2
            total = 0
            important_word = True
            list_important = []
            state_search = False
            actual_word = ""
            #vérification des mots important
            #   on recherche les mots importants
            for x in self.soluc[self.question]:
                if x == "*":
                    state_search = not(state_search)
                else:
                    if state_search:
                        actual_word += x
                    elif actual_word != "":
                        list_important.append(actual_word)
                        actual_word = ""
            #vérification de la proportion des mots juste
            for x in list_important:
                if x in don:
                    pass
                else:
                    important_word = False
                    break
            for x in treated:
                if x in word_resp:
                    total += 1
            if total >= objectif and important_word:
                don = resp
        if don == resp:
            if legit:
                await self.main_window.info_dialog(title=string[0], message=string[1], on_result=self.null)
            else:
                await self.main_window.info_dialog(title=string[0], message=string[2]+self.soluc[self.question].replace('*','')+string[3]+self.entré.value)
            self.essaie = 2
            self.question_passé.append(self.question)
            if self.global_proprety == []:
                await self.lecture_quiz_test()
            else:
                await self.lecture_multi_check()
        else:
            if self.proprety[6] == False:
                self.clear = False
            if self.essaie != 0:
                self.main_window.error_dialog(title=string[4], message=string[5]+self.essaie+string[6])
                self.essaie -= 1
            else:
                self.clear = False
                if (self.proprety[4] and skip != None) or (self.proprety[5] and self.proprety[4]):
                    await self.main_window.error_dialog(string[4], string[7], on_result=self.null)
                else:
                    await self.main_window.error_dialog(title=string[4], message=string[8]+self.soluc[self.question].replace('*','')+string[3]+self.entré.value+string[9], on_result=self.null)
                self.essaie = self.proprety[7]
                if self.global_proprety == []:
                    await self.lecture_quiz_test()
                else:
                    await self.lecture_multi_check()
    async def lecture_QCM_test(self, widget=None):
        string = self.strings[self.language]["QCM_test"]
        if self.global_proprety == []:
            nb_quest = len(self.quest) - 1
            self.num_question = random.randint(0, nb_quest)
            if len(self.question_passé) == nb_quest + 1:
                if self.clear == True:
                    await self.main_window.info_dialog(title=string[0], message=string[1], on_result=self.null)
                warn = await self.main_window.question_dialog(title=string[0], message=string[2], on_result=self.null)
                if warn == True:
                    if current_platform == "android": sys.exit()
                    else: self.main_window.close()
                else:
                    self.question = random.randint(0, nb_quest)
                    self.question_passé = []
                    self.clear = True
            else:
                self.question = random.randint(0, nb_quest)
                while self.question in self.question_passé:
                    self.question = random.randint(0, nb_quest)
        else:
            self.proprety = self.global_proprety[2]
            self.num_question = self.question
        if len(self.proprety) < self.len_proprety_QCM:
            if await self.main_window.confirm_dialog(string[3], string[4], on_result=self.null):
                self.page = 0
                self.mode = "QCM"
                if self.global_proprety == []:
                    await self.création_QCM_question()
                else:
                    await self.création_multi_checker()
            else:
                await self.main_window.error_dialog(string[5], string[6], on_result=self.null)
                self.option_quit()
        question = self.quest[self.num_question]
        self.reponse = self.rep[self.num_question]
        self.option_défintion()
        a_t = (self.num_question)*4 + 0
        b_t = (self.num_question)*4 + 1
        c_t = (self.num_question)*4 + 2
        d_t = (self.num_question)*4 + 3
        self.essaie = 2
        if self.proprety[1]:
            if current_platform == "android": self.titre.text = string[7]
            else:self.titre.text=string[8]
            if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap(question, width=self.width_aide))
            else:self.aide.text=question
            desc_text = string[9]
            del self.desc.style.color
            if self.proprety[2]:
                desc_text += string[10]+len(self.rep[self.num_question])+string[11]
            if current_platform == "android" : self.desc.text="\n".join(textwrap.wrap(desc_text), width=self.width_windows)
            else: self.desc.text = desc_text
            # result = num_question
            if self.global_proprety == []:
                a_b = toga.Button(text=self.soluc[a_t], on_press=lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check="A")))
                b_b = toga.Button(text=self.soluc[b_t], on_press=lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check="B")))
                c_b = toga.Button(text=self.soluc[c_t], on_press=lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check="C")))
                d_b = toga.Button(text=self.soluc[d_t], on_press=lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check="D")))
            else:
                a_b = toga.Button(text=self.soluc[self.num_question][0], on_press=lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check="A")))
                b_b = toga.Button(text=self.soluc[self.num_question][1], on_press=lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check="B")))
                c_b = toga.Button(text=self.soluc[self.num_question][2], on_press=lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check="C")))
                d_b = toga.Button(text=self.soluc[self.num_question][3], on_press=lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check="D")))
            self.main_box.add(self.titre, self.aide, self.desc, a_b, b_b, c_b, d_b, self.bouton1)
        else:
            if current_platform == "android": self.titre.text = string[12]
            else: self.titre.text = string[13]
            if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap(question, width=self.width_aide))
            else: self.aide.text = question
            desc_text = string[14]
            del self.desc.style.color
            if self.proprety[2]:
                desc_text += "\n"+len(self.rep[self.num_question])+string[15]
            if current_platform == "android" : self.desc.text="\n".join(textwrap.wrap(text=str(desc_text), width=self.width_windows))
            else: self.desc.text = desc_text
            a_box = toga.Box(style=Pack(direction = ROW))
            b_box = toga.Box(style=Pack(direction = ROW))
            c_box = toga.Box(style=Pack(direction = ROW))
            d_box = toga.Box(style=Pack(direction = ROW))
            self.A_s = toga.Switch(style=Pack(font_size=12), text="")
            self.B_s = toga.Switch(style=Pack(font_size=12), text="")
            self.C_s = toga.Switch(style=Pack(font_size=12), text="")
            self.D_s = toga.Switch(style=Pack(font_size=12), text="")
            if self.global_proprety == []:
                A_e = toga.Label(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), text = self.soluc[a_t])
                B_e = toga.Label(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), text = self.soluc[b_t])
                C_e = toga.Label(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), text = self.soluc[c_t])
                D_e = toga.Label(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), text = self.soluc[d_t])
            else:
                A_e = toga.Label(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), text = self.soluc[self.num_question][0])
                B_e = toga.Label(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), text = self.soluc[self.num_question][1])
                C_e = toga.Label(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), text = self.soluc[self.num_question][2])
                D_e = toga.Label(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), text = self.soluc[self.num_question][3])
            a_box.add(A_e, self.A_s)
            b_box.add(B_e, self.B_s)
            c_box.add(C_e, self.C_s)
            d_box.add(D_e, self.D_s)
            self.bouton2.text, self.bouton2.on_press = string[16], lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check=None))
            self.main_box.add(self.titre, self.aide, self.desc, a_box, b_box, c_box, d_box, self.bouton2, self.bouton1)
        self.bouton1.text, self.bouton1.on_press = string[17], self.option_aband
    async def lecture_QCM_check(self, to_check:str):
        string = self.strings[self.language]["QCM_check"]
        if self.proprety[1]:
            ok = self.get_rep(to_check, self.rep[self.num_question])
        else:
            ok = (self.A_s.value == self.get_rep("A", self.rep[self.num_question]) and self.B_s.value == self.get_rep("B", self.rep[self.num_question]) and self.C_s.value == self.get_rep("C", self.rep[self.num_question]) and self.D_s.value == self.get_rep("D", self.rep[self.num_question]))
        if ok:
            await self.main_window.info_dialog(title=string[0], message=string[1], on_result=self.null)
            self.essaie = 2
            self.question_passé.append(self.num_question)
            if self.global_proprety == []:
                await self.lecture_QCM_test()
            else:
                await self.lecture_multi_check()
        else:
            self.clear = False
            if self.essaie == 2:
                self.main_window.error_dialog(title=string[2], message=string[3])
                self.essaie = 1
            elif self.essaie == 1:
                self.main_window.error_dialog(title=string[2], message=string[4])
                self.essaie = 0
            elif self.essaie == 0:
                await self.main_window.error_dialog(title=string[2], message=string[5]+self.reponse+"!", on_result=self.null)
                self.essaie = 2
                if self.global_proprety == []:
                    await self.lecture_QCM_test()
                else:
                    await self.lecture_multi_check()
    async def lecture_truefalse_test(self, widget=None):
        string = self.strings[self.language]["truefalse_test"]
        if self.global_proprety == []:
            nb_quest = len(self.quest) - 1
            self.question = random.randint(0, nb_quest)
            if len(self.question_passé) == nb_quest + 1:
                if self.clear == True:
                    await self.main_window.info_dialog(title=string[0], message=string[1], on_result=self.null)
                warn = await self.main_window.question_dialog(title=string[0], message=string[2], on_result=self.null)
                if warn == True:
                    if current_platform == "android": sys.exit()
                    else: self.main_window.close()
                else:
                    self.question = random.randint(0, nb_quest)
                    self.question_passé = []
                    self.clear = True
            else:
                while self.question in self.question_passé:
                    self.question = random.randint(0, nb_quest)
        else:
            self.proprety = self.global_proprety[3]
        self.option_défintion()
        if current_platform == "android": self.titre.text = string[3]
        else:self.titre.text=string[4]
        if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap(self.quest[self.question], width=self.width_aide))
        else:self.aide.text=self.quest[self.question]
        if current_platform == "android" : self.desc.text = "\n".join(textwrap.wrap(string[5], width=self.width_windows))
        else:self.desc.text = string[5]
        del self.desc.style.color
        self.entré_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        self.entré_rep = toga.Switch(style=Pack(font_size=12, font_family="Calibri light", text_align=CENTER, padding_top=10), text="Activer si vrai")
        self.entré_box.add(self.entré_rep)
        self.bouton1.text, self.bouton1.on_press = string[6], self.lecture_truefalse_check
        self.bouton2.text, self.bouton2.on_press = string[7], self.option_aband
        self.main_box.add(self.titre, self.aide, self.desc, self.entré_box, self.bouton1, self.bouton2)
        self.bouton1.focus()
    async def lecture_truefalse_check(self, widget=None):
        string = self.strings[self.language]["truefalse_check"]
        don = self.entré_rep.value
        resp = self.soluc[self.question]
        if don == resp:
            await self.main_window.info_dialog(title=string[0], message=string[1], on_result=self.null)
            self.question_passé.append(self.question)
        else:
            self.clear = False
            await self.main_window.error_dialog(title=string[2], message=string[3], on_result=self.null)
        if self.global_proprety == []:
            await self.lecture_truefalse_test()
        else:
            await self.lecture_multi_check()
    async def lecture_multi_check(self, widget=None):
        nb_quest = len(self.quest) - 1
        self.question = random.randint(0, nb_quest)
        if len(self.question_passé) == nb_quest + 1:
            if self.clear == True:
                await self.main_window.info_dialog(title="Quiz completé!", message="Félicitations, ce quiz a été complété avec un sans faute!", on_result=self.null)
            warn = await self.main_window.question_dialog(title="Quiz completé!", message="Vous avez répondu juste à toutes les questions du quiz!\nVoulez-vous quitter?", on_result=self.null)
            if warn == True:
                if current_platform == "android": sys.exit()
                else: self.main_window.close()
            else:
                self.question = random.randint(0, nb_quest)
                self.question_passé = []
                self.clear = True
        else:
            while self.question in self.question_passé:
                self.question = random.randint(0, nb_quest)
        self.option_défintion()
        last_question = self.soluc[self.question]
        if type(last_question) == str:
            await self.lecture_quiz_test()
        elif type(last_question) == list:
            await self.lecture_QCM_test()
        elif type(last_question) == bool:
            await self.lecture_truefalse_test()
    def get_rep(self, char:str, to_check:str) -> bool:
        for x in to_check:
            if x == char:
                return True
        return False
    def android_startup(self, widget=None):
        string = self.strings[self.language]["android_startup"]
        img_title = toga.Image(f"{self.paths.app}/resources/title.png")
        img = toga.ImageView(img_title, style=Pack(width=300, height=150))
        self.aide.text = string[0]+self.version
        self.bouton1.text, self.bouton1.on_press = string[1], self.android_act
        self.main_box.add(img, self.aide, self.bouton1)
    def android_act(self, widget=None):
        self.width_windows = self.main_window.size[0]//11
        self.width_aide = self.main_window.size[0]//18
        self.option_défintion()
        self.option_main()
        self.option_def_menu()
    def change_state_nav(self, state:bool):
        if current_platform != "android":
            for x in [self.next_page, self.prev_page, self.suppr]:
                x.enabled = state
    def change_title_main_window(self, name, state:bool):
        s_name = self.strings[self.language]["software_name"]
        if state == True:
            self.main_window.title = f"{s_name} - {name}"
        else:
            self.main_window.title = f"{s_name} - {name}*"
        self.save_state = state
    async def close_window(self, widget=None):
        string = self.strings[self.language]["close_window"]
        if self.save_state == False:
            message = await self.main_window.confirm_dialog(string[0], string[1], self.null)
            if message == True:
                self.exit()
        else:
            self.exit()
def main():
    return QuêteduQI(icon="resources/logo.ico")