#!/usr/bin/env python3
from __future__ import print_function
import sys
if sys.version_info[0] == 2:
    import Tkinter as tkinter
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
    tkinter.messagebox = messagebox
    tkinter.filedialog = filedialog
else:
    import tkinter, tkinter.messagebox, tkinter.filedialog

import threading
import re, os, sys

class Regexen(tkinter.Frame):
    exitThread = False
    running = False
    matches = []
    VERSION = "0.1"
    TAGS = [{"fg" : "white", "bg" : "red"},
            {"fg" : "white", "bg" : "green"},
            {"fg" : "white", "bg" : "blue"},
            {"fg" : "black", "bg" : "yellow"},
            {"fg" : "black", "bg" : "lightblue"},
            {"fg" : "black", "bg" : "hotpink"},
            {"fg" : "black", "bg" : "lightgreen"},
            {"fg" : "white", "bg" : "purple1"}]
    REFERENCE = """------- Characters classes
.		Any character
\\.  \\\\		Escaped dot, escaped backslash
\\xFF		Escaped hexadecimal character code
[abc]		Character class ('a', 'b' or 'c')
[^abc]		Negated character class
\d		Digit (0-9)
\w		Word character (digit, a-z or underscore)
\s		Space (space, \\t, \\n)
\D  \W  \S	Negated classes of the above

------- Groups and backreferences
(a)		Group
(a|b)		Either 'a' or 'b'
\\1		Backrefereces to groups (1 to 9)
(?:)		Non-capturing group

------- Repetition
?		Zero or one of the preceding element
*		Zero or more of the preceding element
+		One or more of the preceding element
??  *?  +?		Makes the repetition operator lazy
{n}		Exactly n times
{n,m}		Between n and m times
{n,}		At least n times
{,n}		At most n times

------- Anchors
^		Start of string (or line if 'm' switch)
$		End of string (or line if 'm' switch)
\\b  \\B		Word boundary and its opposite

------- Lookarounds
(?=a)		Positive lookahead (followed by 'a')
(?!a)		Negative lookahead (not followed by 'a')
(?<=a)		Positive lookbehind (preceded by 'a')
(?<!a)		Negative lookbehind (not preceded by 'a')

------- Flags
(?i)  (?s)  (?m)	Case insensitive, dot matches all, multiline"""
    ABOUT = """
Regexen v"""+VERSION+"""

Software distributed under MIT License, read the
accompanying LICENSE.txt file for more information.
    """
    def __init__(self):
        self.root = tkinter.Tk()
        tkinter.Frame.__init__(self, self.root)
    def init(self):
        # Root window
        self.root.title("Regexen v"+self.VERSION)
        self.root.minsize(950,550)
        if os.name == 'nt':
            self.root.option_add('*Dialog.msg.font', 'Courier 14')
        else:
            self.root.option_add('*Dialog.msg.font', 'Courier 7 ')
        # Menu
        self.menuBar = tkinter.Menu(self.root)
        export = tkinter.Menu(self.menuBar,tearoff=0)
        export.add_command(label="Lines", command=self.menuExportLines)
        export.add_command(label="Matches", command=self.menuExportMatches)
        self.menuBar.add_cascade(label="Export", menu =export)
        self.menuBar.add_command(label="Reference", command=self.menuReference_click)
        self.menuBar.add_command(label="About", command=self.menuAbout_click)
        self.root.config(menu=self.menuBar)

        # Left and Right panels
        self.leftPanel = tkinter.Frame(self.root, height=100)
        self.leftPanel.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1, padx=10,pady=10)
        self.rightPanel = tkinter.Frame(self.root, width=300, height=100)
        self.rightPanel.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, padx=10,pady=10)
        # Options Panel #
        self.optionsPanel = tkinter.Frame(self.leftPanel)
        self.optionsPanel.pack(anchor=tkinter.N, fill=tkinter.X)
        # Global option variables
        self.bAutoUpdate      = tkinter.IntVar()
        self.bCaseInsensitive = tkinter.IntVar()
        self.bDotMatchesAll   = tkinter.IntVar()
        self.bMatchLineBreaks = tkinter.IntVar()
        self.bReWordWrap      = tkinter.IntVar()
        self.bTextWordWrap    = tkinter.IntVar()
        # Checkboxes
        self.lblOptions = tkinter.Label(self.optionsPanel, text="Options")
        self.lblOptions.grid(column=0, row=0, sticky=tkinter.NW)
        self.chkboxCaseInsensitive = tkinter.Checkbutton(self.optionsPanel, text = "Case insensitive (i)", variable=self.bCaseInsensitive)
        self.chkboxCaseInsensitive.grid(column=0,row=1, sticky = tkinter.NW)
        self.chkboxMatchLineBreaks = tkinter.Checkbutton(self.optionsPanel, text = "^$ match line breaks (m)", variable=self.bMatchLineBreaks)
        self.chkboxMatchLineBreaks.grid(column=1,row=1, sticky = tkinter.NW)
        self.chkboxDotMatchesAll = tkinter.Checkbutton(self.optionsPanel, text = "Dot matches all (s)" , variable=self.bDotMatchesAll)
        self.chkboxDotMatchesAll.grid(column=2,row=1, sticky = tkinter.NW)
        self.chkboxAutoUpdate = tkinter.Checkbutton(self.optionsPanel, text="Auto update", variable=self.bAutoUpdate)
        self.chkboxAutoUpdate.select()
        self.chkboxAutoUpdate.grid(column=3, row=1, sticky="nw")
        # Run button
        self.btnRunRegex = tkinter.Button(self.optionsPanel, text="   Run   ", command=self.btnRunRegex_click, state=tkinter.DISABLED)
        self.btnRunRegex.grid(column=4, row=1, sticky="e", columnspan=2)
        # Just a spacer
        tkinter.Label(self.optionsPanel).grid(column=6,row=1, sticky="e")
        # Clear button
        self.btnClear  = tkinter.Button(self.optionsPanel, text=" Clear ", command=self.btnClear_click)
        self.btnClear.grid(column=7, row=1, sticky="e", columnspan=2)
        # Trace variables
        self.bAutoUpdate.trace("w", self.toggleRunButton)
        self.bCaseInsensitive.trace("w", self.chkboxGenericToggle)
        self.bMatchLineBreaks.trace("w", self.chkboxGenericToggle)
        self.bDotMatchesAll.trace("w", self.chkboxGenericToggle)
        self.bReWordWrap.trace("w", self.toggleReWordWrap)
        self.bTextWordWrap.trace("w", self.toggleTextWordWrap)

        # Texboxes for input
        tmpFrame = tkinter.Frame(self.leftPanel, height=100)
        self.lblRegexInput = tkinter.Label(tmpFrame, text="Regex")
        self.lblRegexInput.pack(side=tkinter.LEFT, anchor=tkinter.NW)
        self.chkboxReWordWrap = tkinter.Checkbutton(tmpFrame, text="Word wrap", variable=self.bReWordWrap)
        self.chkboxReWordWrap.pack(side=tkinter.TOP, anchor=tkinter.NE)
        tmpFrame.pack(anchor=tkinter.N, fill=tkinter.X)
        self.txtboxInputRegex = tkinter.Text(self.leftPanel, height=3, wrap="none")
        self.txtboxInputRegex.pack(side=tkinter.TOP, anchor=tkinter.NW, fill=tkinter.X, expand=True)

        tmpFrame = tkinter.Frame(self.leftPanel, height=100)
        self.lblSearchText = tkinter.Label(tmpFrame, text="Search text")
        self.lblSearchText.pack(side=tkinter.LEFT, fill=tkinter.Y, anchor=tkinter.W)
        self.chkboxTextWordWrap = tkinter.Checkbutton(tmpFrame, text="Word wrap", variable=self.bTextWordWrap)
        self.chkboxTextWordWrap.pack(side=tkinter.TOP, anchor=tkinter.NE)
        tmpFrame.pack(anchor=tkinter.N, fill=tkinter.X)
        self.txtboxSearchText = xScrolledText(self.leftPanel, height=55, wrap="none")
        self.txtboxSearchText.pack(side=tkinter.TOP, anchor=tkinter.N, fill=tkinter.BOTH, expand=True)
        # Bind key events to textboxes
        self.txtboxSearchText.bind("<KeyRelease>", self.txtboxInputRegex_onkey)
        self.txtboxInputRegex.bind("<KeyRelease>", self.txtboxInputRegex_onkey)
        # Set focus to input regex
        self.txtboxInputRegex.focus()
        # Set up tag for error highlighting
        self.txtboxInputRegex.tag_config("error1", foreground="white", background="red")
        # Set up tags for match highlighting
        for i in range(0, len(self.TAGS)):
            self.txtboxSearchText.tag_config("selection" + str(i+1), foreground=self.TAGS[i]['fg'], background=self.TAGS[i]['bg'])

        # Right panel
        self.lblResults = tkinter.Label(self.rightPanel, text="Results")
        self.lblResults.pack(side=tkinter.TOP,anchor="nw")
        self.lblNumEntries = tkinter.Label(self.rightPanel, text="\n",justify=tkinter.LEFT, wraplength=245, height=4, anchor="n")
        self.lblNumEntries.pack(anchor="nw")
        self.lblTitleGroups = tkinter.Label(self.rightPanel, text="Groups")
        self.lblTitleGroups.pack(anchor="nw")

        # Item selector
        self.selectorFrame = tkinter.Frame(self.rightPanel)
        self.selectorFrame.pack()
        self.btnISFirst = tkinter.Button(self.selectorFrame, text=" First ", state=tkinter.DISABLED, command=self.btnISFirst_click)
        self.btnISFirst.grid(column=0, row=0)
        self.btnISPrev = tkinter.Button(self.selectorFrame, text=" Prev ", state=tkinter.DISABLED, command=self.btnISPrev_click)
        self.btnISPrev.grid(column=1, row=0)
        self.lblISCurrent = tkinter.Label(self.selectorFrame, text=" ".center(25), width=12)
        self.lblISCurrent.grid(column=2, row=0, columnspan=1)
        self.btnISNext = tkinter.Button(self.selectorFrame, text=" Next ", state=tkinter.DISABLED, command=self.btnISNext_click)
        self.btnISNext.grid(column=3, row=0)
        self.btnISLast = tkinter.Button(self.selectorFrame, text=" Last ", state=tkinter.DISABLED, command=self.btnISLast_click)
        self.btnISLast.grid(column=4, row=0)
        self.lblGroups = tkinter.Label(self.rightPanel, text="",justify=tkinter.LEFT,wraplength=245)
        self.lblGroups.pack(anchor="nw")

        # Starting window size
        self.root.geometry("950x500")
    def loop(self):
        # tkinter main loop
        tkinter.mainloop()
    def menuAbout_click(self):
        tkinter.messagebox.showinfo("About", self.ABOUT)
    def menuReference_click(self):
        tkinter.messagebox.showinfo("Quick Reference", self.REFERENCE, icon=None)
    def menuExportLines(self):
        if len(self.matches) == 0:
            tkinter.messagebox.showerror("Error!", "No matches to export.")
            return
        fp = tkinter.filedialog.asksaveasfile(defaultextension=".txt", initialdir=os.curdir, filetypes=[('Text file','*.txt')])
        if fp == None:
            #tkinter.messagebox.showerror("Error!", "An error occured while trying to open the file.")
            return
        stext = re.sub("\n$", "", self.txtboxSearchText.get("1.0", tkinter.END))
        lines = stext.split('\n')
        exportedLines = []
        for r in self.matches:
            tup = self.dec2floatNotation(r.start(), r.end(), stext)
            sline = int(tup[0].split('.')[0])
            eline = int(tup[1].split('.')[0])
            if sline in exportedLines:
                continue
            out = "\n".join(lines[sline-1:eline])
            fp.write(out+"\n")
            exportedLines.append(sline)
        fp.close()
    def menuExportMatches(self):
        if len(self.matches) == 0:
            tkinter.messagebox.showerror("Error!", "No matches to export.")
            return
        fp = tkinter.filedialog.asksaveasfile(defaultextension=".txt", initialdir=os.curdir, filetypes=[('Text file','*.txt')])
        if fp == None:
            #tkinter.messagebox.showerror("Error!", "An error occured while trying to open the file.")
            return
        stext = re.sub("\n$", "", self.txtboxSearchText.get("1.0", tkinter.END))
        for r in self.matches:
            fp.write(stext[r.start():r.end()]+'\n')
        fp.close()
    def txtboxInputRegex_onkey(self, event):
        if self.bAutoUpdate.get() and self.running == False:
            self.runRegex()
    def btnRunRegex_click(self, *args):
        if self.btnRunRegex.config()['text'][4] == ' Cancel ':
            self.exitThread = True
        else:
            self.runRegex()
    def btnISFirst_click(self):
        self.current_match = 0
        self.showGroups()
    def btnISPrev_click(self):
        self.current_match -= 1
        if self.current_match < 0:
            self.current_match = 0
        self.showGroups()
    def btnISNext_click(self):
        self.current_match += 1
        if self.current_match >= len(self.matches):
            self.current_match = len(self.matches)-1
        self.showGroups()
    def btnISLast_click(self):
        self.current_match = len(self.matches)-1
        self.showGroups()
    def toggleReWordWrap(self, *args):
        if self.bReWordWrap.get() == 1:
            self.txtboxInputRegex.config(wrap="char")
        else:
            self.txtboxInputRegex.config(wrap="none")
    def toggleTextWordWrap(self, *args):
        if self.bTextWordWrap.get() == 1:
            self.txtboxSearchText.config(wrap="word")
        else:
            self.txtboxSearchText.config(wrap="none")
    def toggleRunButton(self, *args):
        if self.bAutoUpdate.get() == 1:
            self.btnRunRegex.config(state=tkinter.DISABLED)
        else:
            self.btnRunRegex.config(state=tkinter.ACTIVE)
    def toggleRunningState(self):
        if self.running:
            self.txtboxInputRegex.config(state="disabled")
            self.txtboxSearchText.config(state="disabled")
            self.btnRunRegex.config(state=tkinter.ACTIVE)
            self.btnRunRegex.config(text=" Cancel ")
            self.lblNumEntries['text'] = "...Running..."
        else:
            self.txtboxInputRegex.config(state="normal")
            self.txtboxSearchText.config(state="normal")
            self.btnRunRegex.config(text="   Run   ")
            self.toggleRunButton(self)
    def chkboxGenericToggle(self, *args):
        if self.bAutoUpdate.get():
            self.runRegex()
    def enableItemSelectorButtons(self):
        self.btnISFirst.config(state=tkinter.ACTIVE)
        self.btnISPrev.config(state=tkinter.ACTIVE)
        self.btnISNext.config(state=tkinter.ACTIVE)
        self.btnISLast.config(state=tkinter.ACTIVE)
        self.lblISCurrent.config(state=tkinter.ACTIVE)
    def disableItemSelectorButtons(self):
        self.lblISCurrent['text'] = "".center(25)
        self.btnISFirst.config(state=tkinter.DISABLED)
        self.btnISPrev.config(state=tkinter.DISABLED)
        self.btnISNext.config(state=tkinter.DISABLED)
        self.btnISLast.config(state=tkinter.DISABLED)
        self.lblISCurrent.config(state=tkinter.DISABLED)
    def dec2floatNotation(self, start, end, string):
        rows, rowe = 1, 1
        subs, sube = 0, 0
        i = -1
        while True:
            i = string.find("\n", i+1)
            if i == -1:
                break
            if start > i:
                rows += 1
                subs = (i + 1)
            if end > i:
                rowe += 1
                sube = (i + 1)
        return (str(rows)+"."+str(start-subs), str(rowe)+"."+str(end-sube))
    def btnClear_click(self, *args):
        self.txtboxInputRegex.delete("1.0", tkinter.END)
        self.txtboxSearchText.delete("1.0", tkinter.END)
    def runRegex(self):
        if self.running:
            # Does this ever happen?
            return
        bgtask = threading.Timer(0, self.backgroundRunRegex)
        bgtask.daemon = True
        bgtask.start()
    def showGroups(self):
        if len(self.matches) == 0:
            return
        if self.current_match < 0 or self.current_match >= len(self.matches):
            return
        groups = self.matches[self.current_match].groups()
        if len(groups) == 0:
            return
        self.enableItemSelectorButtons()
        if self.current_match == 0:
            self.btnISFirst.config(state=tkinter.DISABLED)
            self.btnISPrev.config(state=tkinter.DISABLED)
        if self.current_match == len(self.matches)-1:
            self.btnISNext.config(state=tkinter.DISABLED)
            self.btnISLast.config(state=tkinter.DISABLED)
        self.lblGroups["text"] = ""
        self.lblISCurrent['text'] = ("match "+str(self.current_match+1)).center(25)
        group_index = 0
        for i in groups:
            self.lblGroups["text"] += "\\"+str(group_index+1) + ": " + str(i) +"\n"
            group_index += 1
    def cleanup(self):
        # Clean up results
        self.lblGroups['text'] = ""
        self.lblNumEntries['text'] = "\n\n"
        self.lblNumEntries.config(fg="black")
        self.disableItemSelectorButtons()
        # Remove tags
        self.txtboxInputRegex.tag_remove('error1',"1.0", tkinter.END)
        for i in range(0, len(self.TAGS)):
            self.txtboxSearchText.tag_remove('selection'+str(i+1),"1.0", tkinter.END)
    def backgroundRunRegex(self):
        # First do a cleanup
        self.cleanup()
        # Remove \n at the end of the string
        regex = re.sub("\n$", "", self.txtboxInputRegex.get("1.0", tkinter.END))
        stext = re.sub("\n$", "", self.txtboxSearchText.get("1.0", tkinter.END))
        if regex == "" or stext == "":
            return
        # Make sure we have good values for these variables
        self.exitThread = False
        self.running = True
        try:
            flag = 0
            self.matches = []
            self.current_match = 0
            if self.bDotMatchesAll.get() == 1:
                flag = flag | re.DOTALL
            if self.bCaseInsensitive.get() == 1:
                flag = flag | re.IGNORECASE
            if self.bMatchLineBreaks.get() == 1:
                flag = flag | re.MULTILINE
            result = re.findall(regex, stext, flag)
            if result:
                index = 0
                self.toggleRunningState()
                for r in re.finditer(regex, stext, flag):
                    self.matches.append(r)
                    tup = self.dec2floatNotation(r.start(), r.end(), stext)
                    self.txtboxSearchText.tag_add("selection" + str(index % len(self.TAGS)+1), tup[0], tup[1])
                    index += 1
                    # An exitThread "signal" has been sent from the main thread
                    if self.exitThread:
                        break
                self.lblNumEntries['text'] = str(index) + " item(s) found.\n\n"
                self.showGroups()
        except Exception as e:
            # Get last word from e
            # First remove " (line x, column x)" if it exists
            emsg = re.sub(" \(line \d+, column \d+\)$", "", str(e))
            if(re.match("\d+", emsg.split()[-1])):
                pos = int(emsg.split()[-1])
                tup = self.dec2floatNotation(pos, pos+1, regex)
                self.txtboxInputRegex.tag_add("error1", tup[0], tup[1])
            self.lblNumEntries['text'] = "Error compiling regex.\n"+str(e)
            self.lblNumEntries.config(fg="red")
        # If we exited the loop with an exitThread signal, do a cleanup
        if self.exitThread:
            self.cleanup()
        self.running = False
        self.toggleRunningState()

# This class is based on Python tkinter library (Lib\tkinter\scrolledtext.py)
# I only added support for a horizontal scrollbar
class xScrolledText(tkinter.Text):
    def __init__(self, master=None, **kw):
        self.frame = tkinter.Frame(master)
        self.vbar = tkinter.Scrollbar(self.frame)
        self.vbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.hbar = tkinter.Scrollbar(self.frame, orient=tkinter.HORIZONTAL)
        self.hbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        kw.update({'yscrollcommand': self.vbar.set, 'xscrollcommand': self.hbar.set})
        tkinter.Text.__init__(self, self.frame, **kw)
        self.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.vbar['command'] = self.yview
        self.hbar['command'] = self.xview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        if sys.version_info[0] == 2:
            # Add support for Python 2
            text_meths = vars(tkinter.Text).keys()
            methods = vars(tkinter.Pack).keys() + vars(tkinter.Grid).keys() + vars(tkinter.Place).keys()
            methods = set(methods).difference(text_meths)
        else:
            # Python 3
            text_meths = vars(tkinter.Text).keys()
            methods = vars(tkinter.Pack).keys() | vars(tkinter.Grid).keys() | vars(tkinter.Place).keys()
            methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


def loadText(file):
    if not os.path.exists(file):
        print("Error! Invalid file specified.")
        return None
    fp = open(file, 'r')
    lines = fp.read()
    fp.close()
    return lines

# If we're on Windows and the user double clicked the script (as opposed to calling it from a terminal)
# display a message about changing the extension to .pyw to avoid creating a terminal window
if os.name =="nt" and "PROMPT" not in os.environ:
    print("""\n\n\n
    NOTICE

        You can avoid creating this terminal window if you change
    the extension of this script to .pyw""")

app = Regexen()
app.init()

# Load search text
if len(sys.argv) > 1:
    lines = loadText(sys.argv[1])
    app.txtboxSearchText.insert(tkinter.END, lines if lines != None else "")
# Load regex
if len(sys.argv) > 2:
    lines = loadText(sys.argv[2])
    app.txtboxInputRegex.insert(tkinter.END, lines if lines != None else "")

# Main loop
app.loop()
