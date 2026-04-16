# Copilot Chat Prompts - Prerequisites & Setup

Use these prompts in **VS Code Copilot Chat** to verify prerequisites and complete setup.

---

## 📋 **Prerequisites Overview**

Before using the Copilot Chat Exporter, you need:

- ✅ **Windows 10 or later**
- ✅ **Python 3.7 or higher**
- ✅ **VS Code with Copilot Chat** (installed and used)
- ✅ **Git** (to clone the repository)

---

## 🔍 **Prerequisites Check Prompts**

### **Prompt 1: Check if I have everything to run this tool**

```
I want to use the Copilot Chat History Exporter.
Help me verify I have all the prerequisites:
1. What Windows version do I need?
2. How do I check my Windows version?
3. How do I check if Python 3.7+ is installed?
4. How do I check if VS Code has Copilot Chat enabled?
5. Do I need Git installed?

Give me exact steps to verify each requirement.
```

### **Prompt 2: Help me check my Python version**

```
How do I check if Python 3.7 or higher is installed on my Windows computer?
Please give me:
1. The exact command to run
2. What output should I look for?
3. What version numbers are acceptable?
4. Where do I run this command from?
```

### **Prompt 3: VS Code and Copilot Chat - do I have it?**

```
How do I check if I have VS Code installed with Copilot Chat?
Please explain:
1. Where in VS Code can I find Copilot Chat?
2. What if I don't see it - what do I need to do?
3. Is Copilot Chat the same as GitHub Copilot?
4. Do I need a GitHub account?
```

---

## 🔧 **Install Prerequisites Prompts**

### **Prompt 4: Install Python on Windows**

```
I don't have Python installed on my Windows computer.
Guide me through:
1. Where do I download Python?
2. Which Python version should I get (3.7+)?
3. What options should I select during installation?
4. How do I verify it installed correctly?
5. Do I need to do anything special after installation?
```

### **Prompt 5: Install Copilot Chat in VS Code**

```
I have VS Code but don't have Copilot Chat.
Can you help me:
1. Find where to install extensions in VS Code?
2. Search for and install "GitHub Copilot Chat"?
3. Do I need a paid subscription?
4. How do I verify it's installed and working?
```

### **Prompt 6: Install Git on Windows**

```
Do I need Git installed for the Copilot Chat History Exporter?
If yes, please guide me:
1. Where do I download Git?
2. What settings should I use during installation?
3. How do I verify Git is installed?
4. Can I use GitHub Desktop instead?
```

---

## 🚀 **Setup Prompts**

### **Prompt 7: Step-by-step setup after cloning the repo**

```
I've successfully cloned https://github.com/nchandik/copilot-chat-exporter.git to my computer.
Now walk me through the complete setup process:
1. What command do I run first?
2. What questions will the setup ask me?
3. How should I answer each question?
4. What should I do after setup completes?
5. How do I test if it's working?

Please explain each step clearly.
```

### **Prompt 8: Help me decide where to save my chat files**

```
During setup, I need to choose where to save my exported Copilot chats.
Help me understand:
1. What is a good location?
2. Should I use the default location or choose custom?
3. Can I change this later?
4. What if I want to save to OneDrive or Google Drive?
5. What are the pros and cons of each option?
```

### **Prompt 9: Help me set the export time for my timezone**

```
I'm in IST (Indian Standard Time) timezone.
During setup, I need to set a time for daily exports.
Help me decide:
1. What time should I set? (I'm usually working until 6 PM)
2. Does the export time change with daylight saving?
3. What happens if my computer is off at that time?
4. Can I change the time later?
5. Do I need to format the time in any special way?
```

### **Prompt 10: Set up Windows Task Scheduler for daily exports**

```
After running the setup, I need to schedule daily exports.
Guide me through using either:
- Option A: Right-click and run schedule_daily.bat
- Option B: Run schedule_daily.ps1 in PowerShell
- Option C: Manual Task Scheduler setup

Which option is easiest for beginners?
Can you explain what each option does?
```

### **Prompt 11: I completed setup - how do I verify it works?**

```
I've completed the setup for Copilot Chat History Exporter.
How do I verify that everything is working correctly?
Please tell me:
1. What command should I run to test it?
2. What files should be created?
3. Where will those files be saved?
4. What should I look for to confirm success?
5. What if I don't see the expected files?
```

---

## ✅ **Quick Setup Checklist**

Use this as you go through setup:

```
Prerequisites Check:
☐ Windows 10 or later
☐ Python 3.7+ installed
☐ VS Code with Copilot Chat
☐ Git installed (optional but recommended)

Setup Steps:
☐ Clone: git clone https://github.com/nchandik/copilot-chat-exporter.git
☐ Run: python export_copilot_history.py --setup
☐ Answer setup questions (directory, time, timezone)
☐ Run: python export_copilot_history.py (to test)
☐ Schedule with schedule_daily.bat or schedule_daily.ps1

Verification:
☐ Found exported JSON file
☐ Found exported Markdown file
☐ Task Scheduler shows scheduled task
☐ Files contain chat history
```

---

## 🎯 **How to Use These Prompts**

1. **Open Copilot Chat** in VS Code (Ctrl+L or click chat icon)
2. **Copy a prompt** from above
3. **Paste into chat**
4. **Follow the guidance**

---

## 📝 **Prompt Tips**

### **For Custom Questions:**
Feel free to modify prompts with:
- Your actual Windows/Python version
- Your specific timezone
- Your company setup

### **Example:**
```
Original: "I'm in IST timezone..."
Your version: "I'm in PST timezone and work night shift..."
```

---

## 🚀 **Recommended Prompt Order**

1. **First:** Prompt 1 → Check prerequisites
2. **Then:** Prompt 2-3 → Verify what you have
3. **If missing:** Prompt 4-6 → Install missing prerequisites
4. **Finally:** Prompt 7-11 → Complete setup

---

**Ready to start?**  
Use **Prompt 1** first to verify you have everything! ✨

---

For detailed information, see:
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Comprehensive guide
- [README.md](README.md) - Features & usage
- [QUICKSTART.md](QUICKSTART.md) - Quick reference
