// Installeur de l'app du skin (FM27 Vanilla Enhanced Skin) : un seul .exe, compilé par fabriquer.py avec le csc de
// Windows (.NET Framework 4, C# 5 : pas de $"" ni de =>). Contient le dossier de partage (ressource payload.zip) et
// le logo. Installe dans %LOCALAPPDATA%\Programs\FM27 Vanilla Enhanced Skin (pas de droits admin : l'app écrit dans
// son dossier et se met à jour seule), raccourcis Bureau + menu Démarrer, entrée « Désinstaller » dans Windows.
// Réinstallation / version plus récente par-dessus : outils\ remplacé, backups\ (réglages, sauvegardes) gardé.
// Désinstallation : ce même .exe copié dans le dossier (DESINSTALLEUR), lancé avec /desinstaller.
// Setup unique (v1.68) : à l'ouverture, regarde la dernière Release GitHub (même dépôt / token que mise_a_jour.py,
// ressource maj.txt posée par fabriquer.py) ; si elle est plus récente que la version embarquée, son zip est
// téléchargé (sha256 vérifié) et installé à la place. Échec / hors ligne : version embarquée.
// v2.17 : app Rust (outils\app\fm27-serveur.exe), plus de Python dans le Setup (python\ d'une ancienne installation
// laissé tel quel).
using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Management;
using System.Net;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Web.Script.Serialization;
using System.Windows.Forms;
using Microsoft.Win32;

static class Programme
{
    public const string NOM = "FM27 Vanilla Enhanced Skin";
    public const string AUTEUR = "AlexJeuVideal x Kinito";
    public static string CLE = @"Software\Microsoft\Windows\CurrentVersion\Uninstall\FM27VanillaEnhancedSkin";
    // essai (Claude) : /essai "<dossier>" [desinstaller] : sans fenêtre, raccourcis dans <dossier>\raccourcis,
    // clé de registre « -essai », journal <dossier>.log ; jamais le vrai Bureau / la vraie clé
    public static string ESSAI = null;
    public const string DESINSTALLEUR = "Desinstaller - Uninstall.exe";
    public const string LANCEUR = "Lancer - Launch.bat";
    // installeur en anglais pour tout le monde (choix du joueur, 2026-11-12) ; les textes FR restent prêts :
    // CultureInfo.CurrentUICulture.TwoLetterISOLanguageName == "fr" pour suivre la langue de Windows
    public static readonly bool FR = false;

    public static string T(string fr, string en) { return FR ? fr : en; }

    public static string DossierParDefaut()
    {
        return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Programs", NOM);
    }

    public static string Raccourci(Environment.SpecialFolder ou)
    {
        if (ESSAI != null)
            return Path.Combine(ESSAI, "raccourcis", (ou == Environment.SpecialFolder.DesktopDirectory ? "bureau " : "demarrer ") + NOM + ".lnk");
        return Path.Combine(Environment.GetFolderPath(ou), NOM + ".lnk");
    }

    [STAThread]
    static void Main(string[] args)
    {
        if (args.Length > 1 && args[0] == "/essai")
        {
            ESSAI = Path.GetFullPath(args[1]);
            CLE += "-essai";
            string log = ESSAI + ".log";
            try
            {
                if (args.Length > 2 && args[2] == "desinstaller") Desinstallation.Lancer(ESSAI);
                else
                {
                    File.AppendAllText(log, "app fermee : " + Installation.FermerApp(ESSAI) + "\r\n");
                    Directory.CreateDirectory(Path.Combine(ESSAI, "raccourcis"));
                    Action<int, string> avance = delegate (int p, string m) { File.AppendAllText(log, p + " " + m + "\r\n"); };
                    string zip = null, note = null;
                    Maj.Info info = null;
                    try { info = Maj.Derniere(); }
                    catch (Exception ex) { note = "verif en ligne : " + ex.Message; }
                    File.AppendAllText(log, "embarquee " + Installation.Version() + " | en ligne " + (info == null ? "-" : info.Tag) + "\r\n");
                    if (info != null && Maj.PlusRecente(info.V, Maj.VersionDe(Installation.Version())))
                        zip = Maj.Preparer(info, avance, out note);
                    if (note != null) File.AppendAllText(log, "note : " + note + "\r\n");
                    try { Installation.Faire(ESSAI, true, true, avance, zip); }
                    finally { if (zip != null) Installation.Supprimer(zip); }
                    File.AppendAllText(log, "installee " + Installation.VersionInstallee(ESSAI) + " | python " + Installation.PythonPresent() + "\r\nOK\r\n");
                }
            }
            catch (Exception ex) { File.AppendAllText(log, "ERREUR " + ex + "\r\n"); }
            return;
        }
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        if (args.Length > 0 && args[0] == "/desinstaller")
        {
            Desinstallation.Lancer(args.Length > 1 ? args[1] : null);
            return;
        }
        Application.Run(new Fenetre());
    }
}

static class Installation
{
    // version écrite dans outils/commun/version.txt du zip (« … v1.12 … »)
    public static string Version()
    {
        using (ZipArchive z = Ouvrir())
        {
            ZipArchiveEntry e = z.GetEntry("outils/commun/version.txt");
            if (e == null) return "";
            using (StreamReader r = new StreamReader(e.Open()))
            {
                string s = r.ReadToEnd();
                int i = s.IndexOf(" v");
                if (i < 0) return "";
                int j = s.IndexOf(' ', i + 2);
                return j < 0 ? s.Substring(i + 1).Trim() : s.Substring(i + 1, j - i - 1);
            }
        }
    }

    static ZipArchive Ouvrir()
    {
        return new ZipArchive(Assembly.GetExecutingAssembly().GetManifestResourceStream("payload.zip"), ZipArchiveMode.Read);
    }

    // dossier du zip qui contient outils/commun/version.txt ("" = racine) ; null = pas un zip de l'app
    public static string Prefixe(ZipArchive z)
    {
        const string V = "outils/commun/version.txt";
        foreach (ZipArchiveEntry e in z.Entries)
        {
            string n = e.FullName.Replace('\\', '/');
            if (n.EndsWith(V) && (n.Length == V.Length || n[n.Length - V.Length - 1] == '/')) return n.Substring(0, n.Length - V.Length);
        }
        return null;
    }

    public static string VersionInstallee(string dossier)
    {
        try { return File.ReadAllText(Path.Combine(dossier, @"outils\commun\version.txt")).Trim(); }
        catch (Exception) { return "?"; }
    }

    public static void Faire(string dossier, bool bureau, bool demarrer, Action<int, string> avance)
    {
        Faire(dossier, bureau, demarrer, avance, null);
    }

    // zipEnLigne : zip de la Release (téléchargé, vérifié) installé à la place du contenu embarqué, sauf python\
    public static void Faire(string dossier, bool bureau, bool demarrer, Action<int, string> avance, string zipEnLigne)
    {
        Directory.CreateDirectory(dossier);
        string outils = Path.Combine(dossier, "outils");
        bool backupsExistait = Directory.Exists(Path.Combine(dossier, "backups"));
        using (ZipArchive emb = Ouvrir())
        using (ZipArchive web = zipEnLigne == null ? null : ZipFile.OpenRead(zipEnLigne))
        {
            string pre = web == null ? "" : Prefixe(web);
            if (pre == null) throw new InvalidDataException("zip sans outils/commun/version.txt");
            // (zip, préfixe à retirer, python\ seulement ?)
            List<Tuple<ZipArchive, string, bool>> sources = new List<Tuple<ZipArchive, string, bool>>();
            if (web != null) sources.Add(Tuple.Create(web, pre, false));
            sources.Add(Tuple.Create(emb, "", web != null));
            int n = 0, i = 0;
            foreach (Tuple<ZipArchive, string, bool> s in sources) n += s.Item1.Entries.Count;
            if (Directory.Exists(outils))   // ancienne version : remplacée en entier (pas de fichier du joueur dedans)
            {
                avance(5, Programme.T("Suppression de l'ancienne version…", "Removing the old version…"));
                Directory.Delete(outils, true);
            }
            foreach (Tuple<ZipArchive, string, bool> s in sources)
                foreach (ZipArchiveEntry e in s.Item1.Entries)
                {
                    i++;
                    string rel = e.FullName.Replace('\\', '/');
                    if (!rel.StartsWith(s.Item2)) continue;
                    rel = rel.Substring(s.Item2.Length);
                    if (rel.Length == 0 || rel.EndsWith("/") || rel.Contains("..") || rel.Contains(":")) continue;
                    // python\ : toujours celui du Setup (le zip de la Release n'en a pas) ; sans zip en ligne, le
                    // contenu embarqué est posé en entier (bug v1.70 : python\ sauté quand rien n'était téléchargé)
                    if (web != null && s.Item3 != rel.StartsWith("python/")) continue;
                    // backups : marqueurs du choix de base seulement à la 1re installation (sinon les choix du joueur)
                    if (rel.StartsWith("backups/") && backupsExistait) continue;
                    string dest = Path.Combine(dossier, rel.Replace('/', Path.DirectorySeparatorChar));
                    Directory.CreateDirectory(Path.GetDirectoryName(dest));
                    for (int essai = 1; ; essai++)   // fichier tenu un instant (antivirus, app qui finit de se fermer)
                    {
                        try { e.ExtractToFile(dest, true); break; }
                        catch (IOException) { if (essai >= 5) throw; Thread.Sleep(1000); }
                    }
                    if (i % 5 == 0) avance(10 + 75 * i / n, Programme.T("Copie des fichiers…", "Copying files…"));
                }
        }
        avance(88, Programme.T("Raccourcis…", "Shortcuts…"));
        string desinst = Path.Combine(dossier, Programme.DESINSTALLEUR);
        string moi = Assembly.GetExecutingAssembly().Location;
        if (!string.Equals(Path.GetFullPath(moi), Path.GetFullPath(desinst), StringComparison.OrdinalIgnoreCase))
            File.Copy(moi, desinst, true);
        // raccourcis : l'app Rust directement (pas de fenêtre de .bat), sinon le lanceur
        string lanceur = Lanceur(dossier);
        string icone = Path.Combine(dossier, @"outils\app\icone.ico");
        string bur = Programme.Raccourci(Environment.SpecialFolder.DesktopDirectory);
        string dem = Programme.Raccourci(Environment.SpecialFolder.Programs);
        if (bureau) CreerRaccourci(bur, lanceur, dossier, icone); else Supprimer(bur);
        if (demarrer) CreerRaccourci(dem, lanceur, dossier, icone); else Supprimer(dem);
        avance(95, Programme.T("Inscription dans Windows…", "Registering in Windows…"));
        using (RegistryKey k = Registry.CurrentUser.CreateSubKey(Programme.CLE))
        {
            k.SetValue("DisplayName", Programme.NOM + " by " + Programme.AUTEUR);
            k.SetValue("Publisher", Programme.AUTEUR);
            k.SetValue("DisplayIcon", icone);
            k.SetValue("InstallLocation", dossier);
            k.SetValue("UninstallString", "\"" + desinst + "\" /desinstaller");
            k.SetValue("NoModify", 1, RegistryValueKind.DWord);
            k.SetValue("NoRepair", 1, RegistryValueKind.DWord);
        }
        avance(100, Programme.T("Terminé.", "Done."));
    }

    // processus de l'app lancés depuis <dossier> (serveur pythonw de python\ ou .venv\ : il reste 180 s après la
    // page fermée et verrouille python314.dll / les .pyd ; vu en vrai le 2026-10-30) ; chemin de l'exe ou ligne de
    // commande (le pythonw d'un .venv relance le Python de base, hors du dossier)
    public static int[] ProcessusApp(string dossier)
    {
        string d = Path.GetFullPath(dossier).TrimEnd('\\') + "\\";
        int moi = Process.GetCurrentProcess().Id;
        System.Collections.Generic.List<int> ids = new System.Collections.Generic.List<int>();
        try
        {
            using (ManagementObjectSearcher s = new ManagementObjectSearcher("SELECT ProcessId, ExecutablePath, CommandLine FROM Win32_Process"))
                foreach (ManagementObject p in s.Get())
                {
                    int id = Convert.ToInt32(p["ProcessId"]);
                    string exe = p["ExecutablePath"] as string ?? "", cmd = p["CommandLine"] as string ?? "";
                    if (id == moi || exe.EndsWith(DESINST_EXE, StringComparison.OrdinalIgnoreCase)) continue;
                    if (exe.StartsWith(d, StringComparison.OrdinalIgnoreCase) || cmd.IndexOf(d, StringComparison.OrdinalIgnoreCase) >= 0)
                        ids.Add(id);
                }
        }
        catch (Exception) { }   // WMI indisponible : on tente quand même, les essais répétés + le message prennent le relais
        return ids.ToArray();
    }
    const string DESINST_EXE = "\\" + Programme.DESINSTALLEUR;

    // ferme l'app avant de remplacer ses fichiers ; rend le nombre de processus fermés
    public static int FermerApp(string dossier)
    {
        int n = 0;
        foreach (int id in ProcessusApp(dossier))
        {
            try
            {
                using (Process p = Process.GetProcessById(id))
                {
                    p.Kill();
                    p.WaitForExit(5000);
                    n++;
                }
            }
            catch (Exception) { }
        }
        return n;
    }

    public static string Lanceur(string dossier)
    {
        string app = Path.Combine(dossier, APP);
        return File.Exists(app) ? app : Path.Combine(dossier, Programme.LANCEUR);
    }

    static void CreerRaccourci(string lnk, string cible, string dossier, string icone)
    {
        Type t = Type.GetTypeFromProgID("WScript.Shell");
        dynamic shell = Activator.CreateInstance(t);
        dynamic r = shell.CreateShortcut(lnk);
        r.TargetPath = cible;
        r.WorkingDirectory = dossier;
        r.IconLocation = icone + ",0";
        r.WindowStyle = cible.EndsWith(".bat") ? 7 : 1;   // fenêtre du .bat réduite (il se ferme tout de suite)
        r.Description = Programme.NOM;
        r.Save();
    }

    public static void Supprimer(string f)
    {
        try { if (File.Exists(f)) File.Delete(f); } catch (IOException) { } catch (UnauthorizedAccessException) { }
    }

    // v2.17 : l'app est un programme Rust (outils\app\fm27-serveur.exe), plus besoin de Python
    public const string APP = @"outils\app\fm27-serveur.exe";

    // l'app peut s'ouvrir : app Rust dans le Setup ; avant : Python 3.14 livré (python\, v1.21), sinon même recherche
    // que « Lancer - Launch.bat » : pyw ou pythonw dans le PATH
    public static bool PythonPresent()
    {
        using (ZipArchive z = Ouvrir())
            if (z.GetEntry(APP.Replace('\\', '/')) != null || z.GetEntry("python/pythonw.exe") != null) return true;
        string[] noms = { "pyw.exe", "pythonw.exe" };
        foreach (string d in (Environment.GetEnvironmentVariable("PATH") ?? "").Split(';'))
        {
            if (d.Trim().Length == 0) continue;
            foreach (string n in noms)
            {
                try { if (File.Exists(Path.Combine(d.Trim(), n))) return true; } catch (ArgumentException) { }
            }
        }
        return false;
    }
}

// dernière Release GitHub (comme commun\mise_a_jour.py) ; essai : UIPICKER_MAJ_API / _DEPOT / _TOKEN (faux serveur)
static class Maj
{
    public class Info { public string Tag, Nom, Url, Sha256, Sha256Url; public int[] V; public long Taille; }

    static string Depot = "", Token = "", Api = "https://api.github.com";
    static bool Essai;
    const long TAILLE_MAX = 200L * 1024 * 1024;

    static Maj()
    {
        try
        {
            using (Stream s = Assembly.GetExecutingAssembly().GetManifestResourceStream("maj.txt"))
                if (s != null)
                    using (StreamReader r = new StreamReader(s))
                    {
                        Depot = (r.ReadLine() ?? "").Trim();
                        Token = (r.ReadLine() ?? "").Trim();
                    }
        }
        catch (Exception) { }
        string e = Environment.GetEnvironmentVariable("UIPICKER_MAJ_API");
        if (!string.IsNullOrEmpty(e)) { Api = e.TrimEnd('/'); Essai = true; }
        e = Environment.GetEnvironmentVariable("UIPICKER_MAJ_DEPOT");
        if (!string.IsNullOrEmpty(e)) Depot = e;
        e = Environment.GetEnvironmentVariable("UIPICKER_MAJ_TOKEN");
        if (e != null) Token = e;
        ServicePointManager.SecurityProtocol |= SecurityProtocolType.Tls12;
    }

    public static int[] VersionDe(string s)
    {
        Match m = Regex.Match(s ?? "", @"v(\d+)\.(\d+)");
        return m.Success ? new int[] { int.Parse(m.Groups[1].Value), int.Parse(m.Groups[2].Value) } : null;
    }

    public static string Nom(int[] v) { return v == null ? "?" : "v" + v[0] + "." + v[1].ToString("00"); }

    public static bool PlusRecente(int[] a, int[] b)
    {
        if (a == null) return false;
        if (b == null) return true;
        return a[0] > b[0] || (a[0] == b[0] && a[1] > b[1]);
    }

    // redirections suivies à la main : le token ne part que vers l'API (jamais vers le lien signé)
    static HttpWebResponse Get(string url, bool binaire, int delai)
    {
        for (int k = 0; k < 6; k++)
        {
            if (!url.StartsWith("https://") && !Essai) throw new InvalidOperationException("address refused: " + url);
            HttpWebRequest q = (HttpWebRequest)WebRequest.Create(url);
            q.UserAgent = "FM27-Vanilla-Enhanced-Skin";
            q.Accept = binaire ? "application/octet-stream" : "application/vnd.github+json";
            q.AllowAutoRedirect = false;
            q.Timeout = delai;
            q.ReadWriteTimeout = 60000;
            if (Token.Length > 0 && url.StartsWith(Api + "/")) q.Headers["Authorization"] = "Bearer " + Token;
            HttpWebResponse r;
            try { r = (HttpWebResponse)q.GetResponse(); }
            catch (WebException ex)
            {
                r = ex.Response as HttpWebResponse;
                if (r == null) throw;
            }
            int c = (int)r.StatusCode;
            string loc = r.Headers["Location"];
            if (c >= 300 && c < 400 && !string.IsNullOrEmpty(loc))
            {
                r.Close();
                url = new Uri(new Uri(url), loc).ToString();
                continue;
            }
            if (c != 200)
            {
                r.Close();
                throw new WebException("GitHub HTTP " + c);
            }
            return r;
        }
        throw new WebException("too many redirects");
    }

    static string Texte(string url, bool binaire)
    {
        using (HttpWebResponse r = Get(url, binaire, 10000))
        using (StreamReader s = new StreamReader(r.GetResponseStream(), Encoding.UTF8))
            return s.ReadToEnd();
    }

    // null = pas de dépôt réglé
    public static Info Derniere()
    {
        if (Depot.Length == 0) return null;
        JavaScriptSerializer js = new JavaScriptSerializer();
        js.MaxJsonLength = int.MaxValue;
        Dictionary<string, object> d = js.Deserialize<Dictionary<string, object>>(Texte(Api + "/repos/" + Depot + "/releases/latest", false));
        Info i = new Info();
        i.Tag = d.ContainsKey("tag_name") ? d["tag_name"] as string : null;
        i.V = VersionDe(i.Tag);
        if (i.V == null) throw new InvalidDataException("tag without version: " + i.Tag);
        List<Dictionary<string, object>> assets = new List<Dictionary<string, object>>();
        if (d.ContainsKey("assets") && d["assets"] is IEnumerable)
            foreach (object a in (IEnumerable)d["assets"])
                if (a is Dictionary<string, object>) assets.Add((Dictionary<string, object>)a);
        string cle = Token.Length > 0 ? "url" : "browser_download_url";   // dépôt privé : par l'API
        foreach (Dictionary<string, object> a in assets)
        {
            string n = a.ContainsKey("name") ? a["name"] as string ?? "" : "";
            if (!n.ToLowerInvariant().EndsWith(".zip")) continue;
            // v1.70 : la Release a aussi le zip Mac (« … - Mac.zip ») : jamais celui-là
            if (System.Text.RegularExpressions.Regex.IsMatch(n.ToLowerInvariant(), "(^|[^a-z])mac([^a-z]|$)")) continue;
            i.Nom = n;
            i.Url = a[cle] as string;
            i.Taille = a.ContainsKey("size") ? Convert.ToInt64(a["size"]) : 0;
            string dg = a.ContainsKey("digest") ? a["digest"] as string ?? "" : "";
            if (dg.ToLowerInvariant().StartsWith("sha256:")) i.Sha256 = dg.Substring(7).ToLowerInvariant();
            break;
        }
        if (i.Url == null) throw new InvalidDataException("no .zip in release " + i.Tag);
        if (i.Sha256 == null)
            foreach (Dictionary<string, object> a in assets)
                if (string.Equals(a["name"] as string, i.Nom + ".sha256", StringComparison.OrdinalIgnoreCase))
                    i.Sha256Url = a[cle] as string;
        return i;
    }

    // télécharge + vérifie le zip ; rend son chemin, ou null (note = pourquoi) : on installe alors la version embarquée
    public static string Preparer(Info i, Action<int, string> avance, out string note)
    {
        note = null;
        string zip = Path.Combine(Path.GetTempPath(), "FM27VES-" + i.Tag + ".zip");
        try
        {
            string attendu = i.Sha256;
            if (attendu == null && i.Sha256Url != null)
                attendu = Texte(i.Sha256Url, true).Trim().Split(' ', '\t', '\r', '\n')[0].ToLowerInvariant();
            if (attendu == null || !Regex.IsMatch(attendu, "^[0-9a-f]{64}$")) throw new InvalidDataException("no sha256 for the zip");
            if (i.Taille > TAILLE_MAX) throw new InvalidDataException("zip too big");
            string msg = Programme.T("Téléchargement de " + i.Tag + "…", "Downloading " + i.Tag + "…");
            avance(0, msg);
            using (SHA256 h = SHA256.Create())
            {
                using (HttpWebResponse r = Get(i.Url, true, 30000))
                using (Stream s = r.GetResponseStream())
                using (FileStream f = File.Create(zip))
                {
                    long total = r.ContentLength > 0 ? r.ContentLength : i.Taille, lu = 0;
                    byte[] b = new byte[256 * 1024];
                    int n, dernier = -1;
                    while ((n = s.Read(b, 0, b.Length)) > 0)
                    {
                        lu += n;
                        if (lu > TAILLE_MAX) throw new InvalidDataException("zip too big");
                        h.TransformBlock(b, 0, n, null, 0);
                        f.Write(b, 0, n);
                        int p = total > 0 ? (int)Math.Min(100, lu * 100 / total) : 0;
                        if (p != dernier) { dernier = p; avance(p, msg + " " + p + " %"); }
                    }
                }
                h.TransformFinalBlock(new byte[0], 0, 0);
                string vu = BitConverter.ToString(h.Hash).Replace("-", "").ToLowerInvariant();
                if (vu != attendu) throw new InvalidDataException("hash mismatch (file damaged or altered)");
            }
            using (ZipArchive z = ZipFile.OpenRead(zip))
                if (Installation.Prefixe(z) == null) throw new InvalidDataException("not an app zip");
            return zip;
        }
        catch (Exception ex)
        {
            Installation.Supprimer(zip);
            note = ex.Message;
            return null;
        }
    }
}

static class Couleurs
{
    public static readonly Color Fond = Color.FromArgb(8, 17, 27);
    public static readonly Color Panneau = Color.FromArgb(18, 27, 39);
    public static readonly Color Texte = Color.FromArgb(238, 240, 244);
    public static readonly Color Texte2 = Color.FromArgb(164, 171, 184);
    public static readonly Color Violet = Color.FromArgb(177, 69, 227);
    public static readonly Color Rose = Color.FromArgb(229, 15, 81);
    public static readonly Color Ambre = Color.FromArgb(240, 165, 58);
}

class Fenetre : Form
{
    TextBox chemin;
    CheckBox bureau, demarrer, ouvrir;
    Button installer, annuler, parcourir;
    ProgressBar barre;
    Label etat, sous;
    string version;
    bool fini;
    Thread verif;
    Maj.Info enLigne;   // dernière Release, si plus récente que la version embarquée

    public Fenetre()
    {
        version = Installation.Version();
        Text = Programme.NOM + " " + version + " - " + Programme.T("Installation", "Setup");
        Icon = Icon.ExtractAssociatedIcon(Assembly.GetExecutingAssembly().Location);
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false;
        StartPosition = FormStartPosition.CenterScreen;
        AutoScaleMode = AutoScaleMode.Dpi;
        ClientSize = new Size(600, 440);
        BackColor = Couleurs.Fond;
        ForeColor = Couleurs.Texte;
        Font = new Font("Segoe UI", 9.5f);

        PictureBox logo = new PictureBox();
        logo.Image = Image.FromStream(Assembly.GetExecutingAssembly().GetManifestResourceStream("logo.png"));
        logo.SizeMode = PictureBoxSizeMode.Zoom;
        logo.SetBounds(28, 24, 64, 64);
        Controls.Add(logo);

        Label titre = new Label();
        titre.Text = Programme.NOM;
        titre.Font = new Font("Segoe UI", 17f, FontStyle.Bold);
        titre.AutoSize = true;
        titre.Location = new Point(106, 26);
        Controls.Add(titre);

        sous = new Label();
        sous.Text = version + "  ·  by " + Programme.AUTEUR + "  ·  " + Programme.T("Skin pour Football Manager 27", "Skin for Football Manager 27");
        sous.ForeColor = Couleurs.Texte2;
        sous.AutoSize = true;
        sous.Location = new Point(109, 64);
        Controls.Add(sous);

        Label lDossier = new Label();
        lDossier.Text = Programme.T("Dossier d'installation", "Install folder");
        lDossier.Font = new Font("Segoe UI", 9.5f, FontStyle.Bold);
        lDossier.AutoSize = true;
        lDossier.Location = new Point(28, 116);
        Controls.Add(lDossier);

        chemin = new TextBox();
        chemin.Text = DossierInstalle() ?? Programme.DossierParDefaut();
        chemin.BackColor = Couleurs.Panneau;
        chemin.ForeColor = Couleurs.Texte;
        chemin.BorderStyle = BorderStyle.FixedSingle;
        chemin.SetBounds(28, 140, 440, 28);
        Controls.Add(chemin);

        parcourir = Bouton(Programme.T("Parcourir…", "Browse…"), false);
        parcourir.SetBounds(478, 138, 94, 28);
        parcourir.Click += delegate
        {
            using (FolderBrowserDialog d = new FolderBrowserDialog())
            {
                d.Description = Programme.T("Choisis où installer l'app (un dossier « " + Programme.NOM + " » y sera créé).",
                                            "Choose where to install the app (a « " + Programme.NOM + " » folder will be created there).");
                if (d.ShowDialog(this) == DialogResult.OK)
                    chemin.Text = Path.Combine(d.SelectedPath, Programme.NOM);
            }
        };
        Controls.Add(parcourir);

        Label aide = new Label();
        aide.Text = Programme.T("Pas de droits admin. Réglages et sauvegardes du jeu gardés. Version plus récente en ligne ? Elle est prise toute seule.",
                                "No admin rights needed. Settings and game backups are kept. Newer version online? It is fetched automatically.");
        aide.ForeColor = Couleurs.Texte2;
        aide.SetBounds(28, 174, 544, 40);
        Controls.Add(aide);

        bureau = Case(Programme.T("Raccourci sur le Bureau", "Desktop shortcut"), 220);
        demarrer = Case(Programme.T("Raccourci dans le menu Démarrer", "Start menu shortcut"), 246);
        ouvrir = Case(Programme.T("Ouvrir l'app à la fin", "Open the app when done"), 272);

        etat = new Label();
        etat.ForeColor = Couleurs.Texte2;
        etat.SetBounds(28, 300, 544, 56);   // 3 lignes : un message d'échec (chemin long) + le conseil
        if (!Installation.PythonPresent())
        {
            etat.ForeColor = Couleurs.Ambre;
            // 3.14 : UnityPy / lz4 / brotli sans roue Windows pour 3.15 (2026-11-12)
            etat.Text = Programme.T("Python n'a pas été trouvé : installe Python 3.14 depuis python.org (pas 3.15, trop récent ; cocher « Add python.exe to PATH ») avant d'ouvrir l'app.",
                                    "Python was not found: install Python 3.14 from python.org (not 3.15, too new; tick « Add python.exe to PATH ») before opening the app.");
        }
        else etat.Text = Programme.T("Recherche d'une version plus récente en ligne…", "Checking online for a newer version…");
        Controls.Add(etat);
        bool python = Installation.PythonPresent();
        Shown += delegate
        {
            verif = new Thread(delegate ()
            {
                Maj.Info i = null;
                string err = null;
                try { i = Maj.Derniere(); }
                catch (Exception ex) { err = ex.Message; }
                bool plus = i != null && Maj.PlusRecente(i.V, Maj.VersionDe(version));
                if (plus) enLigne = i;
                try
                {
                    BeginInvoke((Action)delegate
                    {
                        if (barre.Visible || !python) return;   // installation déjà lancée / message Python gardé
                        if (plus)
                        {
                            etat.ForeColor = Couleurs.Texte;
                            etat.Text = Programme.T("Version plus récente trouvée en ligne (" + i.Tag + ") : elle sera téléchargée et installée.",
                                                    "Newer version found online (" + i.Tag + "): it will be downloaded and installed.");
                            sous.Text = Maj.Nom(i.V) + "  ·  by " + Programme.AUTEUR + "  ·  " + Programme.T("Skin pour Football Manager 27", "Skin for Football Manager 27");
                            Text = Programme.NOM + " " + Maj.Nom(i.V) + " - " + Programme.T("Installation", "Setup");
                        }
                        else if (err != null)
                            etat.Text = Programme.T("Vérification en ligne impossible : la version " + version + " de ce Setup sera installée (l'app proposera la mise à jour ensuite).",
                                                    "Could not check online: version " + version + " from this Setup will be installed (the app will offer the update afterwards).");
                        else etat.Text = Programme.T("C'est la dernière version.", "This is the latest version.");
                    });
                }
                catch (Exception) { }   // fenêtre déjà fermée
            });
            verif.IsBackground = true;
            verif.Start();
        };

        barre = new ProgressBar();
        barre.SetBounds(28, 360, 544, 8);
        barre.Visible = false;
        Controls.Add(barre);

        annuler = Bouton(Programme.T("Annuler", "Cancel"), false);
        annuler.SetBounds(358, 384, 100, 34);
        annuler.Click += delegate { Close(); };
        Controls.Add(annuler);

        installer = Bouton(Programme.T("Installer", "Install"), true);
        installer.SetBounds(468, 384, 104, 34);
        installer.Click += delegate { Lancer(); };
        Controls.Add(installer);
        AcceptButton = installer;
        ActiveControl = installer;   // sinon le chemin s'ouvre tout surligné
    }

    // dossier d'une installation précédente (registre), pour réinstaller au même endroit
    static string DossierInstalle()
    {
        using (RegistryKey k = Registry.CurrentUser.OpenSubKey(Programme.CLE))
        {
            string d = k == null ? null : k.GetValue("InstallLocation") as string;
            return !string.IsNullOrEmpty(d) && Directory.Exists(d) ? d : null;
        }
    }

    Button Bouton(string texte, bool principal)
    {
        Button b = new Button();
        b.Text = texte;
        b.FlatStyle = FlatStyle.Flat;
        b.FlatAppearance.BorderColor = principal ? Couleurs.Rose : Color.FromArgb(60, 70, 85);
        b.BackColor = principal ? Couleurs.Rose : Couleurs.Panneau;
        b.ForeColor = Color.White;
        b.Font = new Font("Segoe UI", 9.5f, principal ? FontStyle.Bold : FontStyle.Regular);
        b.Cursor = Cursors.Hand;
        return b;
    }

    CheckBox Case(string texte, int y)
    {
        CheckBox c = new CheckBox();
        c.Text = texte;
        c.Checked = true;
        c.AutoSize = true;
        c.Location = new Point(28, y);
        Controls.Add(c);
        return c;
    }

    void Lancer()
    {
        if (fini) { Close(); return; }
        string dossier = chemin.Text.Trim();
        try { dossier = Path.GetFullPath(dossier); }
        catch (Exception)
        {
            MessageBox.Show(this, Programme.T("Ce dossier n'est pas valide.", "This folder is not valid."), Text);
            return;
        }
        string pf = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles);
        string pf86 = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86);
        if (dossier.StartsWith(pf, StringComparison.OrdinalIgnoreCase) || (pf86.Length > 0 && dossier.StartsWith(pf86, StringComparison.OrdinalIgnoreCase)))
        {
            MessageBox.Show(this, Programme.T("« Program Files » est protégé par Windows : l'app ne pourrait pas y garder ses réglages ni se mettre à jour. Garde le dossier proposé.",
                                              "« Program Files » is protected by Windows: the app could not keep its settings there nor update itself. Keep the suggested folder."), Text);
            return;
        }
        if (File.Exists(Path.Combine(dossier, "Outils FM.bat")))
        {
            MessageBox.Show(this, Programme.T("Ce dossier est un dossier de travail : choisis-en un autre.", "This is a work folder: choose another one."), Text);
            return;
        }
        if (Installation.ProcessusApp(dossier).Length > 0)
        {
            if (MessageBox.Show(this, Programme.T("L'app est encore ouverte : il faut la fermer pour la mettre à jour. La fermer maintenant ?",
                                                  "The app is still open: it must be closed to update it. Close it now?"),
                                Text, MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return;
            Installation.FermerApp(dossier);
        }
        installer.Enabled = annuler.Enabled = parcourir.Enabled = chemin.Enabled = false;
        bureau.Enabled = demarrer.Enabled = ouvrir.Enabled = false;
        barre.Visible = true;
        etat.ForeColor = Couleurs.Texte2;
        bool b = bureau.Checked, d = demarrer.Checked;
        Thread v = verif;
        Thread t = new Thread(delegate ()
        {
            Action<int, string> avance = delegate (int p, string m) { BeginInvoke((Action)delegate { barre.Value = p; etat.Text = m; }); };
            string zip = null, note = null;
            try
            {
                if (v != null) v.Join(20000);   // vérif trop longue : version embarquée
                Maj.Info i = enLigne;
                if (i != null)
                {
                    zip = Maj.Preparer(i, avance, out note);
                    if (zip == null)
                        note = Programme.T("Téléchargement de " + i.Tag + " impossible (" + note + ") : la version " + version + " du Setup a été installée, l'app proposera la mise à jour.",
                                           "Could not download " + i.Tag + " (" + note + "): version " + version + " from this Setup was installed, the app will offer the update.");
                }
                Installation.Faire(dossier, b, d, avance, zip);
                BeginInvoke((Action)delegate { Fin(dossier, null, note); });
            }
            catch (Exception ex)
            {
                BeginInvoke((Action)delegate { Fin(dossier, ex, null); });
            }
            finally
            {
                if (zip != null) Installation.Supprimer(zip);
            }
        });
        t.IsBackground = true;
        t.Start();
    }

    void Fin(string dossier, Exception ex, string note)
    {
        if (ex != null)
        {
            etat.ForeColor = Couleurs.Rose;
            etat.Text = Programme.T("Échec : ", "Failed: ") + ex.Message + Programme.T(" (l'app est peut-être ouverte : ferme-la avec Quitter et recommence)",
                                                                                     " (the app may be open: close it with Quit and try again)");
            installer.Enabled = annuler.Enabled = parcourir.Enabled = chemin.Enabled = true;
            bureau.Enabled = demarrer.Enabled = ouvrir.Enabled = true;
            return;
        }
        fini = true;
        etat.ForeColor = Couleurs.Texte;
        etat.Text = Programme.T("C'est installé ! Lance l'app avec le raccourci « " + Programme.NOM + " ».",
                                "Installed! Start the app with the « " + Programme.NOM + " » shortcut.");
        if (note != null)
        {
            etat.ForeColor = Couleurs.Ambre;
            etat.Text += "\n" + note;
            barre.Visible = false;   // place pour le message (jusqu'aux boutons)
            etat.Height = 80;
        }
        installer.Text = Programme.T("Terminer", "Finish");
        installer.Enabled = true;
        if (ouvrir.Checked && Installation.PythonPresent())
        {
            string l = Installation.Lanceur(dossier);
            ProcessStartInfo p = new ProcessStartInfo(l);
            p.WorkingDirectory = dossier;
            p.WindowStyle = l.EndsWith(".bat") ? ProcessWindowStyle.Minimized : ProcessWindowStyle.Normal;
            p.UseShellExecute = true;
            try { Process.Start(p); } catch (Exception) { }
        }
    }
}

static class Desinstallation
{
    static void Dire(string m)
    {
        if (Programme.ESSAI != null) File.AppendAllText(Programme.ESSAI + ".log", "desinstaller : " + m.Replace("\n", " ") + "\r\n");
        else MessageBox.Show(m, Programme.NOM);
    }

    public static void Lancer(string dossier)
    {
        string moi = Assembly.GetExecutingAssembly().Location;
        if (dossier == null)   // lancé depuis le dossier installé : copie dans %TEMP% pour pouvoir tout effacer
        {
            dossier = Path.GetDirectoryName(moi);
            string copie = Path.Combine(Path.GetTempPath(), "FM27VES-desinstaller.exe");
            File.Copy(moi, copie, true);
            Process.Start(copie, "/desinstaller \"" + dossier + "\"");
            return;
        }
        if (File.Exists(Path.Combine(dossier, "Outils FM.bat")) || !File.Exists(Path.Combine(dossier, Programme.LANCEUR)))
        {
            Dire(Programme.T("Ce dossier ne ressemble pas à une installation de l'app : rien n'est supprimé.",
                             "This folder does not look like an app install: nothing is removed."));
            return;
        }
        string q = Programme.T(
            "Désinstaller " + Programme.NOM + " ?\n\nL'app, ses réglages et ses sauvegardes des fichiers d'origine du jeu seront supprimés.\n\n" +
            "Le skin, lui, reste dans le jeu. Pour remettre FM27 d'origine : ferme FM, puis dans Steam, clic droit sur Football Manager 27 > Propriétés > Fichiers installés > « Vérifier l'intégrité des fichiers du jeu ».",
            "Uninstall " + Programme.NOM + "?\n\nThe app, its settings and its backups of the game's original files will be removed.\n\n" +
            "The skin stays in the game. To get the original FM27 back: close FM, then in Steam, right-click Football Manager 27 > Properties > Installed Files > « Verify integrity of game files ».");
        if (Programme.ESSAI == null && MessageBox.Show(q, Programme.NOM, MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return;
        Thread.Sleep(800);   // le .exe du dossier vient de se fermer
        Installation.FermerApp(dossier);
        Installation.Supprimer(Programme.Raccourci(Environment.SpecialFolder.DesktopDirectory));
        Installation.Supprimer(Programme.Raccourci(Environment.SpecialFolder.Programs));
        try
        {
            Directory.Delete(dossier, true);
        }
        catch (Exception ex)
        {
            Dire(Programme.T("Impossible de tout supprimer (l'app est peut-être ouverte : ferme-la avec Quitter et recommence).\n\n",
                             "Could not remove everything (the app may be open: close it with Quit and try again).\n\n") + ex.Message);
            return;
        }
        Registry.CurrentUser.DeleteSubKeyTree(Programme.CLE, false);
        Dire(Programme.T(Programme.NOM + " est désinstallé.", Programme.NOM + " is uninstalled."));
    }
}
