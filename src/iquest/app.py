import toga, os, json, random, asyncio, textwrap, sys, subprocess
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from toga.platform import current_platform
if current_platform == "android":
    from android.content import Intent
    from java import jarray, jbyte
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
    def startup(self):
        self.quest = []
        self.soluc = []
        self.proprety = []
        self.rep = []
        self.reponse = []
        self.version_warn = False
        rang = 0
        self.essaie = 2
        self.question_passé = []
        self.page = 0
        #version = 2.0
        self.main_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, flex=1))

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

        if current_platform == "android":
            self.width_windows = 40
            self.width_aide = 20
            path = str(self.app.paths.data).split("/")
            user = path[3]
            self.android_path = f"/storage/emulated/{user}/documents/Quizs/"
            if not(os.path.exists(self.android_path)):
                os.makedirs(self.android_path)
        self.option_défintion() 
        self.option_main()
        self.option_def_menu()
    def error1(self, widget):
        self.main_window.error_dialog("Erreur", "Cette action n'est pas possible pour le moment! Veuillez entrer au moins une question puis une réponse!")
    def error2(self, widget):
        self.main_window.error_dialog("Erreur", "Cette fonctionnalité n'est pas disponible pour le moment! Vous êtes sur une version de dévellopement")
    def nav_question_sup(self, widget):
        del self.quest[self.page], self.soluc[self.page]
        self.création_question_rafraichir()
    def nav_question_previous(self, widget):
        self.page -= 1
        self.création_question_rafraichir()
    def nav_question_next(self, widget):
        self.page += 1
        self.création_question_rafraichir()
    def nav_QCM_sup(self, widget):
        a_t = (self.page)*4 + 1
        b_t = (self.page)*4 + 2
        c_t = (self.page)*4 + 3
        d_t = (self.page)*4 + 4
        del self.quest[self.page], self.soluc[a_t], self.soluc[b_t], self.soluc[c_t], self.soluc[d_t]
        self.création_QCM_question()
    def nav_QCM_previous(self, widget):
        self.page -= 1
        self.création_QCM_question()
    def nav_QCM_next(self, widget):
        self.page += 1
        self.création_QCM_question()
    def option_défintion(self, widget=None):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        self.main_window.content = self.main_box
        self.titre = toga.Label(text="Menu principal", style=Pack(font_family="Calibri light", font_size=30, text_align=CENTER))
        self.aide = toga.Label(text="Comment ça marche?", style=Pack(font_family="Calibri light", font_size=20, text_align=CENTER))
        self.desc = toga.Label(text="Ce logiciel simple à utiliser vous permettra de réviser en faisait des quizs réalisés par vous ou par des camarades\n Appuyer sur \"Créer un quiz\" pour créer un quiz et laisser-vous guider...\n Si au contraire vous avez déjà un quiz, appuyer sur \"Importer un quiz\" Pour ouvrir un quiz déjà existant!", style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER, padding=10))
        self.bouton1 = toga.Button(text="Créer un quiz", style=Pack(width=300, padding=(20, 0, 5, 0)), on_press=self.création_Créer)
        self.bouton3 = toga.Button(text="Importer quiz", style=Pack(width=300, padding=(5, 0, 20, 0)), on_press=self.null)
        self.bouton2 = toga.Button(text="Modifier quiz", style=Pack(width=300), on_press=self.null) #self.modifier_main)
    def option_taille(self, widget=None):
        self.main_window.info_dialog("Debug",f"Taille de la fenêtre: {self.main_window.size}")
    def option_skip(self, widget):
        self.essaie = 0
        self.lecture_quiz_check()
    def option_def_menu(self, widget=None):
        file = toga.Group("Fichier")
        action = toga.Group("Action")
        debug = toga.Group("Debug")
        cmd4 = toga.Command(self.save, "Enregistrer", tooltip="Enregistrer votre questionnaire", group=file, order=1)
        cmd5 = toga.Command(self.save_to, "Enregistrer sous", tooltip="Choisir un emplacement de sauvegarde", group=file, order=2)
        cmd1 = toga.Command(self.création_Créer, "Créer quiz", tooltip="Lancer la création d'un quiz", group=action, order=1)
        cmd2 = toga.Command(self.modifier_load, "Modifier quiz", tooltip="Importer un quiz et le mofifier", group=action, order=2)
        cmd3 = toga.Command(self.lecture_load, "Importer quiz", tooltip="Faîtes vous testé en important un quiz", group=action, order=3)
        cmd6 = toga.Command(self.option_reset, "Menu", tooltip="Accéder au menu", group=action, order=4)
        cmd7 = toga.Command(self.option_taille, "Taille", tooltip="Afficher la taille de la fenêtre", group=debug)
        if current_platform == "windows":self.commands.add(cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7)
        else: self.main_window.toolbar.add(cmd1, cmd2, cmd3, cmd5)
    def option_quit(self, widget=None):
        if current_platform == "android":
            sys.exit()
        else:
            self.main_window.close()
    def option_main(self, widget=None):
        self.fichier = ""
        self.titre.text = "Menu principal"
        self.aide.text="Comment ça marche?"
        if current_platform == "android":
            self.desc.text="\n".join(textwrap.wrap("Ce logiciel simple à utiliser vous permettra de réviser en faisait des quizs réalisés par vous ou par des camarades\n Appuyer sur \"Créer un quiz\" pour créer un quiz et laisser-vous guider...\n Si au contraire vous avez déjà un quiz, appuyer sur \"Importer un quiz\" Pour ouvrir un quiz déjà existant!", width=self.width_windows))
        else: self.desc.text = "Ce logiciel simple à utiliser vous permettra de réviser en faisait des quizs réalisés par vous ou par des camarades\n Appuyer sur \"Créer un quiz\" pour créer un quiz et laisser-vous guider...\n Si au contraire vous avez déjà un quiz, appuyer sur \"Importer un quiz\" Pour ouvrir un quiz déjà existant!"
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
    def null(self, widget=None, var=None):
        pass
    async def option_quit_save(self, widget):
        warn = await self.main_window.question_dialog("Voulez-vous quitter", "Voulez-vous continuer? Toute données non sauvegardé sera perdu", on_result=self.null)
        if warn == True:
            if current_platform == "android": sys.exit()
            else: self.main_window.close()
    async def option_aband(self, widget=None):
        message = await self.main_window.question_dialog("Quitter", "Voulez-vous quitter le logiciel ?", on_result=self.null)
        if message == True:
            if current_platform == "android":sys.exit()
            else: self.main_window.close()
    def création_Créer(self, widget):
        #self.main_window.info_dialog("Debug",f"Chemin: {self.app.paths.data}")
        self.option_défintion()
        self.titre.text="Création d'un quiz"
        if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap("Quelle type de questionnaire crée?", width=self.width_aide))
        else:self.aide.text="Quelle type de questionnaire crée?"
        if current_platform == "android": self.desc.text= "\n".join(textwrap.wrap("Explications:\nLes questions simple sont des quizs où l'utilisateur devra entrer la réponse au clavier\nLes QCM sont des questions où l'utlisateur devra répondre A, B, C ou D", width=self.width_windows))
        else: self.desc.text = "Explications:\nLes questions simple sont des quizs où l'utilisateur devra entrer la réponse au clavier\nLes QCM sont des questions où l'utlisateur devra répondre A, B, C ou D"
        self.bouton1.text="Questions simples"
        self.bouton1.on_press= self.création_question_rafraichir
        self.bouton2.text="QCM (Choix multiples)"
        self.bouton2.on_press = self.création_QCM_question
        self.bouton3.text, self.bouton3.on_press ="Quitter", self.option_quit
        self.main_box.add(self.titre, self.aide, self.desc, self.bouton1, self.bouton2, self.bouton3)
    def création_question_rafraichir(self, widget=None):
        self.mode = "simple"
        self.phase = "quest"
        if self.proprety == []:
            self.proprety = ["simple", False, False, False]
        self.option_défintion()
        #self.option_def_menu()
        if self.page == len(self.quest): 
            if current_platform == "android": self.titre.text = "Créer"
            else:self.titre.text="Créer une question"
        else: 
            if current_platform == "android": self.titre.text = "Modifier"
            else: self.titre.text="Modificer une question"
        if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap("Veuillez entrer une question", width=self.width_aide))
        else:self.aide.text="Veuillez entrer une question"
        if current_platform == "android": self.desc.text= "\n".join(textwrap.wrap("Veuillez indiquez dans le champ ci-dessous votre question\nAppuyer ensuite sur \"Valider question\" pour entrer une réponse", width=self.width_windows))
        else:self.desc.text="Veuillez indiquez dans le champ ci-dessous votre question\nAppuyer ensuite sur \"Valider question\" pour entrer une réponse"
        self.entré = toga.TextInput(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), on_confirm=self.création_question_soluc)
        if self.page < len(self.quest):
            self.entré.value = self.quest[self.page]
        self.bouton1.text, self.bouton1.on_press = "Valider question", self.création_question_soluc
        self.bouton1.style.update(font_family="Calibri light", font_size=12)
        self.bouton2.text, self.bouton2.on_press = "Terminer", self.save
        self.bouton2.style.update(font_family="Calibri light", font_size=12)
        self.bouton3 = toga.Button(text="Quitter", on_press=self.option_quit_save, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER, width=300, padding=(5, 0, 20, 0)))
        self.nav = toga.Box(Pack(direction=ROW))
        self.del_button = toga.Button(text="Supprimer\nla question", on_press=self.nav_question_sup, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
        self.next_button = toga.Button(text="Suivant", on_press=self.nav_question_next ,style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
        self.previous_button = toga.Button(text="Précédent", on_press=self.nav_question_previous, style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER))
        self.nav.add(self.previous_button, self.del_button, self.next_button)
        if self.page == 0: self.previous_button.enabled = False
        else: self.previous_button.enabled = True
        if self.page == len(self.quest): self.next_button.enabled, self.del_button.enabled = False, False
        else: self.next_button.enabled, self.del_button.enabled = True, True
        self.option_text = toga.Label(text="Options:", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER))
        self.select_canva = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
        self.checkbox_select = toga.Switch(text="Aide à la réponse", style=Pack(font_family="Calibri light", font_size=12, text_align=CENTER), on_change=self.change_check)
        help_select = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press=self.help_select_window)
        self.inclusive_canva = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
        self.checkbox_inclusive = toga.Switch(text="L'essentiel compte!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
        help_inclusive = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_inclusive_window)
        self.shift_canva = toga.Box(style=Pack(direction=ROW, text_align=CENTER))
        self.checkbox_shift = toga.Switch(text="Pas besoins de majuscule!", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_change=self.change_check)
        help_shift = toga.Button(text="?", style=Pack(font_family="Calibri light", font_size=11, text_align=CENTER), on_press= self.help_shift_window)
        self.checkbox_select.value, self.checkbox_inclusive.value, self.checkbox_shift.value = self.proprety[1:4]
        self.select_canva.add(self.checkbox_select, help_select)
        self.inclusive_canva.add(self.checkbox_inclusive, help_inclusive)
        self.shift_canva.add(self.checkbox_shift, help_shift)
        self.nav.add(
        self.previous_button,
        self.del_button,
        self.next_button
        )
        self.main_box.add(self.titre, self.aide, self.desc, self.entré, self.bouton1, self.bouton2, self.bouton3, self.nav, self.option_text, self.select_canva, self.inclusive_canva, self.shift_canva)
    def change_check(self, widget):
        self.proprety = [self.mode, self.checkbox_select.value, self.checkbox_inclusive.value, self.checkbox_shift.value]
    def change_check_QCM(self, widget):
        self.proprety = [self.mode, self.mutiple_switch.value, self.number_rep_switch.value]
    def création_question_soluc(self, widget):
        actuel = self.entré.value
        if actuel == "":
            self.main_window.error_dialog(title="Impossible de continuer", message="Aucune question n'a été entré!")
        else:
            self.main_box.remove(self.nav, self.shift_canva, self.inclusive_canva, self.select_canva, self.option_text, self.bouton2)
            self.phase = "soluc"
            self.aide.text="Veuillez entrer une réponse"
            if current_platform == "android": self.desc.text = "\n".join(textwrap.wrap("Veuillez indiquez dans le champ en dessous la réponse adéquate a votre question\nAppuyer ensuite sur \"Valider question\" pour entrer une autre question\nSi votre quiz est fini, appuyer sur \"Terminer\"\nRépondre \\ pour annuler question", width=self.width_windows))
            else:self.desc.text="Veuillez indiquez dans le champ en dessous la réponse adéquate a votre question\nAppuyer ensuite sur \"Valider question\" pour entrer une autre question\nSi votre quiz est fini, appuyer sur \"Terminer\"\nRépondre \\ pour annuler question"
            if self.page == len(self.quest): self.quest = self.quest + [actuel]
            else: self.quest[self.page] = actuel
            self.entré.value, self.entré.on_confirm = "", self.création_question_question
            if self.page < len(self.soluc):
                self.entré.value = self.soluc[self.page]
            self.bouton1.on_press = self.création_question_question
    async def création_question_question(self, widget):
        self.phase = "quest"
        actuel = self.entré.value
        if actuel == "\\":
            demande = await self.main_window.confirm_dialog(title="Annuler question",message="Êtes vous sur de vouloir annuler votre question?", on_result=self.null)
            if demande == True:
                del self.quest[self.page]
                try:
                    del self.soluc[self.page]
                except IndexError:
                    print("soluc[page] non supprimé car l'index est introuvable")
                self.création_question_rafraichir()
        elif actuel == "":
            self.main_window.error_dialog(title="Impossible de continuer", message="Aucune réponse n'a été entré")
        elif actuel != "":
            self.phase = "quest"
            if self.page == len(self.soluc): 
                self.soluc = self.soluc + [actuel]
                self.page += 1
            else: self.soluc[self.page] = actuel
            self.création_question_rafraichir()
            # entré.delete("0","end")
            # bouton1.config(text = "Valider question", on_press=création.question.réponse)
    async def save(self, widget):
        #actuel = self.entré.value
        warn = await self.main_window.question_dialog(title="Sauvegarder?", message="Voulez sauvegarder maintenant?", on_result=self.null)
        #save = False
        if self.quest != [] and self.soluc != []:
            if current_platform == "android" and warn == True:
                self.titre.text = "Sauvegarder"
                self.aide.text = "Choisir un nom\nde fichier"
                self.desc.text = "\n".join(textwrap.wrap("Veuillez entrer un nom de questionnaire puis appuyez sur \"Sauvegarder\" pour lancer la sauvegarde\nPour modifier un questionnaire précedemment crée, entrez à nouveau son nom, puis validez!", width=self.width_windows))
                self.entré.value = "Sans nom"
                self.bouton1.on_press, self.bouton1.text = self.file_selected, "Sauvegarder"
                self.main_box.remove(self.bouton2, self.bouton3, self.nav) 
                if self.mode == "simple": self.main_box.remove(self.option_text, self.inclusive_canva, self.select_canva, self.shift_canva)
                self.main_window.info_dialog("Restrictions Android", "Dû aux restrictions Android, il n'est pas possible de choisir l'emplacement de sauvegarde du fichier. Les quizs sont sauvegardé dans \"Espace partagé/documents/Quizs/\"")
            else:
                if warn:
                    if self.fichier == "":
                        self.fichier = await self.main_window.save_file_dialog(title="Sauvegarder le questionnaire", suggested_filename="Sans nom.json" ,file_types=["json"], on_result=self.file_selected)
                    else:
                        await self.file_selected()
        else:
            self.main_window.error_dialog("Impossible de sauvegarder", "Votre questionnaire est incomplet, assurez vous d'en avoir déjà importé ou crée un")
    async def file_selected(self, widget=None, dontknown=None):
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
            if self.mode == "simple": self.proprety = [self.mode, self.checkbox_select.value, self.checkbox_inclusive.value, self.checkbox_shift.value]
            else: self.proprety = [self.mode, self.mutiple_switch.value, self.number_rep_switch.value]
            dico["proprety"] = self.proprety
            dico["quest"] = self.quest
            dico["soluc"] = self.soluc
            if self.proprety[0] == "QCM":
                dico["rep"] = self.rep
            if self.fichier != "":
                try:
                    with open (str(self.fichier),'w') as fichie:
                        fichie.write(json.dumps(dico, indent=4))
                except PermissionError:
                    self.main_window.error_dialog(title="Permission non accordée!", message="Vous n'avez pas les permissions de sauvegarder ici! Vérifier que vous avez les droits ou choisissez un autre emplacement!")
                else:
                    await self.main_window.info_dialog(title="Enregistrement réussi!", message="Votre questionnaire a correctement été enregistré!")
                    await self.option_aband()
        else:
            self.main_window.error_dialog(title="Aucun nom de fichier", message="Le fichier n'a pas été enregistré car aucun nom de fichier n'a été entré!")
        if self.mode == "simple": self.création_question_rafraichir()
        else: self.création_QCM_question()
    async def save_to(self, widget):
        #actuel = self.entré.value
        warn = await self.main_window.question_dialog(title="Sauvegarder?", message="Voulez sauvegarder maintenant?", on_result=self.null)
        #save = False
        if self.quest != [] and self.soluc != []:
            if current_platform == "android" and warn == True:
                self.titre.text = "Sauvegarder"
                self.aide.text = "Choisir un nom\nde fichier"
                self.desc.text = "\n".join(textwrap.wrap("Veuillez entrer un nom de questionnaire puis appuyer sur \"Sauvegarder\" pour lancer la sauvegarde\nPour modifier un questionnaire précedemment crée, entrer à nouveau son nom, puis validé!", width=self.width_windows))
                self.entré
                self.bouton1.on_press = self.file_selected
                self.main_box.remove(self.bouton2, self.bouton3, self.nav, self.option_text, self.inclusive_canva, self.select_canva, self.shift_canva)
                self.main_window.info_dialog("Restrictions Android", "Dû aux restrictions Android, il n'est pas possible de choisir l'emplacement de sauvegarde du fichier. Les quizs sont sauvegardé dans \"Espace partagé/documents/Quizs/\"")
            else:
                if warn:
                    self.fichier = await self.main_window.save_file_dialog(title="Sauvegarder le questionnaire", suggested_filename="Sans nom.json" ,file_types=["json"], on_result=self.file_selected)
        else:
            self.main_window.error_dialog("Impossible de sauvegarder", "Votre questionnaire est incomplet, assurez vous d'en avoir déjà importé ou crée un") 
    def help_select_window(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="Si vous activez cette option, lors du test pour ce questionnaire, l'utilisateur pourra accéder à une liste de toute les réponses disponible de ce questionnaire et pourra sélectionner celle qui lui semble le mieux!")
    def help_inclusive_window(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="Si vous activez cette option, lors du test pour ce questionnaire, si la moitié ou plus (qu'importe l'ordre) des mots de la réponse, correspondent à la réponse de la question, la réponse donnée en sera validée\nUtile si le questionnaire contient beaucoup de réponses avec des phrases comprennant plusieurs mots\nNB: Cette fonctionnalitée est expérimentale et peut ne pas fonctionner correctement")
    def help_shift_window(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="Si vous activez cette option, lors du test pour ce questionnaire, une réponse pourra être validée, même si l'utilisateur ne respecte pas les majuscules (et minuscules)\nUtile si les majuscules de vos réponses ne sont pas importantes!")
    def help_multiple_window(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="Si cette option est activée, l'utilisateur devra choisir une réponse parmi les 4 disponibles, si il choisit une des bonnes réponses, la question en sera validée.\nLorsque l'option est désactivée, l'utilisateur devra sélectionner toutes les réponses qu'il juge correct, ATTENTION: Il devra valider TOUTES les bonnes réponses")
    def help_number_rep_window(self, widget):
        self.main_window.info_dialog(title="Aide de l'option", message="Si cette option est activée, l'utilisateur sera tenu informé du nombre de réponses possibles")
    def création_QCM_question(self, widget=None):
        self.phase = "quest"
        self.mode = "QCM"
        self.option_défintion()
        if self.proprety == []:
            self.proprety = [self.mode, False]
        if self.page == len(self.quest): 
            self.titre.text="Créer un QCM"
            if current_platform == "android": self.desc.text = "\n".join(textwrap.wrap("La création d'un QCM se joue en 3 étapes", width=self.width_aide))
            else:self.aide.text = "La création d'un QCM se joue en 3 étapes"
        else: self.titre.text="Modifier un QCM"
        if current_platform == "android": self.desc.text = "\n".join(textwrap.wrap("Pour l'instant, vous devez entrer une question", width=self.width_windows))
        else:self.desc.text="Pour l'instant, vous devez entrer une question"
        self.entré = toga.TextInput(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), on_confirm=self.création_QCM_soluc)
        if self.page < len(self.quest):
            self.entré.value = self.quest[self.page]
        self.bouton1.text, self.bouton1.on_press = "Valider question", self.création_QCM_soluc
        self.bouton2.text, self.bouton2.on_press = "Terminer QCM", self.save
        self.bouton3.text, self.bouton3.on_press = "Quitter", self.option_quit_save
        self.nav = toga.Box(style=Pack(direction = ROW))
        next_button = toga.Button(text="Suivant", on_press=self.nav_QCM_next)
        previous_button = toga.Button(text="Précédent", on_press=self.nav_QCM_previous)
        del_button = toga.Button(text="Supprimer\nla question", on_press=self.nav_QCM_sup)
        self.option_text = toga.Label(text="Options:", style=Pack(font_size=12, font_family="Calibri light", text_align=CENTER))
        self.mutiple_canva = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        try: self.mutiple_switch = toga.Switch(style=Pack(font_family="Calibri light", font_size=12), text="Choix unique", on_change=self.change_check_QCM, value=self.proprety[1])
        except IndexError: 
            self.proprety.append(False)
            self.création_QCM_question()
        self.help_multiple = toga.Button(style=Pack(font_family="Calibri light", font_size=12), text="?", on_press=self.help_multiple_window)
        self.mutiple_canva.add(self.mutiple_switch, self.help_multiple)
        self.number_rep_canva = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        try: self.number_rep_switch = toga.Switch(style=Pack(font_family="Calibri light", font_size=12), text="Indiquer le nombre de réponse", on_change=self.change_check_QCM, value=self.proprety[2])
        except IndexError: 
            self.proprety.append(False)
            self.création_QCM_question()
        self.help_number_rep = toga.Button(style=Pack(font_family="Calibri light", font_size=12), text="?", on_press=self.help_number_rep_window)
        self.number_rep_canva.add(self.number_rep_switch, self.help_number_rep)
        if self.page == 0: previous_button.enabled = False
        else: previous_button.enabled = True
        if self.page == len(self.quest): next_button.enabled, del_button.enabled = False, False
        else: next_button.enabled, del_button.enabled = True, True
        self.nav.add(previous_button, del_button, next_button)
        self.main_box.add(self.titre, self.aide, self.desc, self.entré, self.bouton1, self.bouton2, self.bouton3, self.nav, self.option_text, self.mutiple_canva, self.number_rep_canva)
    def création_QCM_soluc(self, widget):
        if self.entré.value == "":
            self.main_window.error_dialog(title="Question incorrecte", message="Aucune question n'a été entré! Veuillez en entrer une!")
        else:
            self.phase = "soluc"
            self.question = self.entré.value
            self.option_défintion()
            self.titre.text = "Créer un QCM"
            if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap("Vous devez maintenant entrer 4 réponses possibles", width=self.width_aide))
            else:self.aide.text = "Nous devons maintenant connaitre les 4 réponses possibles\nSi vous voulez créer un QCM avec 2 ou 3 réponses possible uniquement,\nmettez \"rien\" ou un / pour montrer que cela n'est pas une réponse possible"
            if current_platform == "android": self.desc.text = "\n".join(textwrap.wrap("Vous devez rentrer ci-dessus, les 4 réponses possible avec 1 bonne réponse et 3 mauvaise réponse\nL'utilisateur devra choisir une réponse (en espérant que ce soit la bonne)", width=self.width_windows))
            else:self.desc.text = "Vous devez rentrer ci-dessus, les 4 réponses possible avec 1 bonne réponse et 3 mauvaise réponse\nL'utilisateur devra choisir une réponse (en espérant que ce soit la bonne)"
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
                self.A_e.value = self.soluc[a_t]
                self.B_e.value = self.soluc[b_t]
                self.C_e.value = self.soluc[c_t]
                self.D_e.value = self.soluc[d_t]
                self.A_s.value = self.get_rep("A", self.rep[self.page])
                self.B_s.value = self.get_rep("B", self.rep[self.page])
                self.C_s.value = self.get_rep("C", self.rep[self.page])
                self.D_s.value = self.get_rep("D", self.rep[self.page])
            self.bouton1.text, self.bouton1.on_press = "Valider réponse", self.création_QCM_at_save
            #bouton2.config(text = "Terminer", command=option.null)
            self.bouton3.text, self.bouton3.on_press = "Quitter", self.option_quit_save
            self.main_box.add(self.titre, self.aide, self.a_box, self.b_box, self.c_box, self.d_box, self.desc, self.bouton1, self.bouton3)
    def création_QCM_at_save(self, widget):
        if (self.A_s.value == False and self.B_s.value == False and self.C_s.value == False and self.D_s.value == False) or (self.A_e.value == "" or self.B_e.value == "" or self.C_e.value == "" or self.D_e.value == ""):
            self.main_window.error_dialog("Impossible de valider", "Assurez-vous d'avoir remplie tous les champs et d'avoir sélectionné au moins une réponse!")
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
                self.main_window.info_dialog("Rétrocompatibilité indisponible", "Malgré la prise en charge du format JSON, les versions 1.3 et 1.3.1 ne peuvent pas lire les QCMs avec plusieurs réponses possible!\nAssurez-vous de lire le QCM sur une version >= 2.0. Autrement, il ne vous sera pas possible de lire le QCM!")
                self.version_warn = True
            if len(self.quest) == self.page:
                for x in self.A_e.value, self.B_e.value, self.C_e.value, self.D_e.value:
                    self.soluc.append(x)
                self.quest.append(self.question)
                self.rep.append(rep)
                self.page += 1
            else:
                self.quest[self.page] = self.question
                self.rep[self.page] = (rep)
                a_t = (self.page)*4 + 0
                b_t = (self.page)*4 + 1
                c_t = (self.page)*4 + 2
                d_t = (self.page)*4 + 3
                self.soluc[a_t] = self.A_e.value
                self.soluc[b_t] = self.B_e.value
                self.soluc[c_t] = self.C_e.value
                self.soluc[d_t] = self.D_e.value
            self.création_QCM_question()
    async def modifier_load(self, widget):
        self.page = 0
        if current_platform == "android":
            suite = True
            content = await self.android_read()
            #self.main_window.info_dialog("Debug", "Content: "+str(content)+"\nContent décodé: "+content.decode("utf_8"))
            try:
                dico = json.loads(str(content.decode("utf-8")))
            except json.JSONDecodeError:
                self.main_window.error_dialog(title="Erreur JSON", message="Impossible d'ouvrir ce questionnaire car le fichier JSON est corrompu!")
                suite = False
            try:
                self.proprety = dico["proprety"]
                self.quest = dico["quest"]
                self.soluc = dico["soluc"]
                if self.proprety[0] == "QCM": self.rep = dico["rep"]
            except (KeyError, IndexError):
                self.main_window.error_dialog(title="Erreur de format", message="Certaines données présente dans le fichier sont incorrectes! Impossible d'ouvrir le questionnaire!")
                suite = False
            if suite == True:
                if self.proprety[0] == "simple":
                    self.création_question_rafraichir()
                else:
                    self.création_QCM_question()
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
            self.fichier = await self.main_window.open_file_dialog(title="Ouvrir un questionnaire", file_types=["json"], on_result=self.modifier_load_selected)
    def modifier_load_selected(self, widget=None, dontknown=None):
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
                if self.proprety[0] == "QCM": self.rep = dico["rep"]
            except (KeyError, IndexError):
                self.main_window.error_dialog(title="Erreur de format", message="Certaines données présente dans le fichier sont incorrectes! Impossible d'ouvrir le questionnaire!")
                suite = False
            if suite == True:
                if self.proprety[0] == "simple":
                    self.création_question_rafraichir()
                else:
                    self.création_QCM_question()
        else:
            self.main_window.error_dialog(title="Aucun fichier choisie", message="Vous n'avez pas choisie de fichier lorsque cela l'a été demandé!")
    async def lecture_load(self, widget):
        self.page = 0
        if current_platform == "android":
            suite = True
            content = await self.android_read()
            #self.main_window.info_dialog("Debug", "Content: "+str(content)+"\nContent décodé: "+content.decode("utf_8"))
            try:
                dico = json.loads(str(content.decode("utf-8")))
            except json.JSONDecodeError:
                self.main_window.error_dialog(title="Erreur JSON", message="Impossible d'ouvrir ce questionnaire car le fichier JSON est corrompu!")
                suite = False
            try:
                self.proprety = dico["proprety"]
                self.quest = dico["quest"]
                self.soluc = dico["soluc"]
                if self.proprety[0] == "QCM": self.rep = dico["rep"]
            except (KeyError, IndexError):
                self.main_window.error_dialog(title="Erreur de format", message="Certaines données présente dans le fichier sont incorrectes! Impossible d'ouvrir le questionnaire!")
                suite = False
            if suite == True:
                self.clear = True
                if self.proprety[0] == "simple":
                    await self.lecture_quiz_test()
                else:
                    await self.lecture_QCM_test()
        else:
            self.fichier = await self.main_window.open_file_dialog(title="Ouvrir un questionnaire", file_types=["json"], on_result=self.lecture_load_selected)
    async def lecture_load_selected(self, widget=None, dontknown=None):
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
                if self.proprety[0] == "QCM": self.rep = dico["rep"]
            except (KeyError, IndexError):
                self.main_window.error_dialog(title="Erreur de format", message="Certaines données présente dans le fichier sont incorrectes! Impossible d'ouvrir le questionnaire!")
                suite = False
            if suite == True:
                self.clear = True
                if self.proprety[0] == "simple":
                    await self.lecture_quiz_test()
                else:
                    await self.lecture_QCM_test()
        else:
            self.main_window.error_dialog(title="Aucun fichier choisie", message="Vous n'avez pas choisie de fichier lorsque cela l'a été demandé!")
    async def lecture_quiz_test(self, widget=None):
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
        if current_platform == "android": self.titre.text = "Répond à\nla question:"
        else:self.titre.text="Répond à la question suivante:"
        if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap(self.quest[self.question], width=self.width_aide))
        else:self.aide.text=self.quest[self.question]
        if current_platform == "android" : self.desc.text = "\n".join(textwrap.wrap("Répondez dans le champs ci-dessous! Pour valider la réponse appuyer sur \"Valider\"", width=self.width_windows))
        else:self.desc.text = "Répondez dans le champs ci-dessous! Pour valider la réponse appuyer sur \"Valider\""
        if self.proprety[2] or self.proprety[3]:
            text = "Ce questionnaire est concerné par des changements de règle:"
            if self.proprety[2]:
                text += "\nSi la moitié des mots de la réponse sont entré, la réponse est validé"
            if self.proprety[3]:
                text += "\nLes majuscules et les minuscules n'ont pas d'importance dans la validation de la réponse"
            if current_platform == "android": self.desc.text = "\n".join(textwrap.wrap(text, width=self.width_windows))
            else:self.desc.text=text
            self.desc.style.update(color="#FF0000")
        self.entré = toga.TextInput(style=Pack(font_family = "Calibri light", font_size = 12, width=300), on_confirm=self.lecture_quiz_check)
        self.bouton1.text, self.bouton1.on_press = "Valider", self.lecture_quiz_check
        self.passer = toga.Button(text="Passer",on_press=self.option_skip, style=Pack(width=300))
        self.bouton2.text, self.bouton2.on_press = "Quitter", self.option_aband
        self.help_canva = toga.Box(style=Pack(direction = ROW))
        self.main_box.add(self.titre, self.aide, self.desc, self.entré, self.bouton1, self.passer, self.bouton2)
        if self.proprety[1]:
            self.option_menu = toga.Selection(style=Pack(width=200), items=["Choisir une réponse"]+self.soluc, value="Choisir une réponse")
            insert_button = toga.Button(text="Insérer cette réponse", on_press= lambda widget: setattr(self.entré, 'value', self.option_menu.value))
            self.help_canva.add(self.option_menu, insert_button)
            self.main_box.add(self.help_canva)
        else:
            cannot = toga.Label(text="L'option d'aide à la réponse a été désactivée pour ce questionnaire", style=Pack(font_family="Calibri light", font_size=12, text_align = CENTER))
            if current_platform == "android": cannot.text = "\n".join(textwrap.wrap("L'option d'aide à la réponse a été désactivée pour ce questionnaire", width=self.width_windows))
            self.main_box.add(cannot)
    async def lecture_quiz_check(self, widget):
        don = self.entré.value
        resp = self.soluc[self.question]
        if self.proprety[3]:
            don = don.lower()
            resp = self.soluc[self.question].lower()
        if self.proprety[2]:
            word = []
            treated = resp.split(" ")
            for x in treated:
                if (x in don.split(" ")) and (not(x in word)):
                    word += x
            if len(word) >= len(treated)//2 and len(word) != 0:
                don = resp
        if don == resp:
            await self.main_window.info_dialog(title="Bonne réponse", message="La réponse donné est juste! Nous allons passé à la question suivante", on_result=self.null)
            self.essaie = 2
            self.question_passé.append(self.question)
            await self.lecture_quiz_test()
        else:
            self.clear = False
            if self.essaie == 2:
                self.main_window.error_dialog(title="Mauvaise réponse", message=f"La réponse donné est fausse!\nIl vous reste {self.essaie} essais\nAttention à l'orthographe, la ponctuation et les majuscules")
                self.essaie -= 1
            elif self.essaie == 1:
                self.main_window.error_dialog(title="Mauvaise réponse", message=f"La réponse donné est fausse!\nIl vous reste {self.essaie} essai\nAttention à l'orthographe, la ponctuation et les majuscules")
                self.essaie = 0
            elif self.essaie == 0:
                await self.main_window.error_dialog(title="Mauvaise réponse", message=f"La bonne réponse est: {self.soluc[self.question]}\nNous allons passé à la question suivante", on_result=self.null)
                self.essaie = 2
                await self.lecture_quiz_test()
    async def lecture_QCM_test(self, widget=None):
        nb_quest = len(self.quest) - 1
        self.num_question = random.randint(0, nb_quest)
        self.question = ""
        if len(self.question_passé) == nb_quest + 1:
            if self.clear == True:
                await self.main_window.info_dialog(title="Quiz completé!", message="Félicitations, ce quiz a été complété avec un sans faute!", on_result=self.null)
            warn = await self.main_window.question_dialog(title="Quiz completé!", message="Vous avez répondu juste à toutes les questions du quiz!\nVoulez-vous quitter?", on_result=self.null)
            if warn == True:
                if current_platform == "android": sys.exit()
                else: self.main_window.close()
            else:
                self.num_question = random.randint(0, nb_quest)
                self.question_passé = []
                self.clear = True
        else:
            while self.num_question in self.question_passé:
                self.num_question = random.randint(0, nb_quest)
        question = self.quest[self.num_question]
        self.reponse = self.rep[self.num_question]
        self.option_défintion()
        a_t = (self.num_question)*4 + 0
        b_t = (self.num_question)*4 + 1
        c_t = (self.num_question)*4 + 2
        d_t = (self.num_question)*4 + 3
        try:
            if self.proprety[1]:
                if current_platform == "android": self.titre.text = "Choisie\nune réponse"
                else:self.titre.text="Choisie une réponse"
                if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap(question, width=self.width_aide))
                else:self.aide.text=question
                desc_text = "Cliquez sur la bonne réponse"
                if self.proprety[2]:
                    desc_text += f"\nIl y a {len(self.rep[self.num_question])} réponse(s) possible(s)"
                if current_platform == "android" : self.desc.text="\n".join(textwrap.wrap(desc_text), width=self.width_windows)
                else: self.desc.text = desc_text
                # result = num_question
                a_b = toga.Button(text=self.soluc[a_t], on_press=lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check="A")))
                b_b = toga.Button(text=self.soluc[b_t], on_press=lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check="B")))
                c_b = toga.Button(text=self.soluc[c_t], on_press=lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check="C")))
                d_b = toga.Button(text=self.soluc[d_t], on_press=lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check="D")))
                self.main_box.add(self.titre, self.aide, self.desc, a_b, b_b, c_b, d_b, self.bouton1)
            else:
                if current_platform == "android": self.titre.text = "Sélectionne\nla(les) réponse(s)"
                else: self.titre.text = "Sélectionne la(les) réponse(s)"
                if current_platform == "android": self.aide.text = "\n".join(textwrap.wrap(question, width=self.width_aide))
                else: self.aide.text = question
                desc_text = "Sélectionner une ou plusieurs réponse qui vous semble correct, en les cochants\npuis appuyez sur \"Confirmer\" pour lancer l'examination de votre réponse"
                if self.proprety[2]:
                    desc_text += f"\n{len(self.rep[self.num_question])} réponse(s) est(sont) attendu(s)"
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
                A_e = toga.Label(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), text = self.soluc[a_t])
                B_e = toga.Label(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), text = self.soluc[b_t])
                C_e = toga.Label(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), text = self.soluc[c_t])
                D_e = toga.Label(style=Pack(font_family="Calibri light", font_size=12, width=300, text_align=CENTER), text = self.soluc[d_t])
                a_box.add(A_e, self.A_s)
                b_box.add(B_e, self.B_s)
                c_box.add(C_e, self.C_s)
                d_box.add(D_e, self.D_s)
                self.bouton2.text, self.bouton2.on_press = "Confirmer", lambda widget, self=self: asyncio.create_task(self.lecture_QCM_check(to_check=None))
                self.main_box.add(self.titre, self.aide, self.desc, a_box, b_box, c_box, d_box, self.bouton2, self.bouton1)
        except IndexError:
            if await self.main_window.confirm_dialog("Questionnaire obsolète", "Ce questionnaire est expiré et n'est plus compatible avec cette version!\nMettez-le à jour puis réessayer!\nLa mise à jour est automatiquement réalisé lorsque vous enregistrer votre quiz, voulez-vous accéder à l'éditeur de quiz afin de sauvegarder et mettre à jour votre QCM?", on_result=self.null):
                self.page = 0
                self.mode = "QCM"
                self.création_QCM_question()
            else:
                await self.main_window.error_dialog("Impossible de lire le QCM", "Votre QCM comporte une erreur de donnée, et ne peux être lu. Modifiez-le dans l'éditeur, puis réessayer!", on_result=self.null)
                self.option_quit()
        self.bouton1.text, self.bouton1.on_press = "Quitter", self.option_aband
    async def lecture_QCM_check(self, to_check:str):
        if self.proprety[1]:
            ok = self.get_rep(to_check, self.rep[self.num_question])
        else:
            ok = (self.A_s.value == self.get_rep("A", self.rep[self.num_question]) and self.B_s.value == self.get_rep("B", self.rep[self.num_question]) and self.C_s.value == self.get_rep("C", self.rep[self.num_question]) and self.D_s.value == self.get_rep("D", self.rep[self.num_question]))
        if ok:
            await self.main_window.info_dialog(title="Bonne réponse", message="Il s'agit de la bonne réponse!\nNous allons passer à la question suivante", on_result=self.null)
            self.essaie = 2
            self.question_passé.append(self.num_question)
            await self.lecture_QCM_test()
        else:
            self.clear = False
            if self.essaie == 2:
                self.main_window.error_dialog(title="Mauvaise réponse", message="Ce n'est pas la bonne réponse!\nIl reste 2 essais!")
                self.essaie = 1
            elif self.essaie == 1:
                self.main_window.error_dialog(title="Mauvaise réponse", message="Ce n'est pas la bonne réponse!\nIl reste 1 essai!")
                self.essaie = 0
            elif self.essaie == 0:
                await self.main_window.error_dialog(title="Mauvaise réponse", message=f"Ce n'est pas la bonne réponse!\nLa bonne réponse était la case: {self.reponse}!", on_result=self.null)
                self.essaie = 2
                await self.lecture_QCM_test()
    def get_rep(self, char:str, to_check:str) -> bool:
        for x in to_check:
            if x == char:
                return True
        return False
def main():
    return QuêteduQI(icon="resources/logo.ico")