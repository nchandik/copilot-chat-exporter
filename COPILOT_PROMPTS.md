# Copilot Chat Prompts for Setup & Usage

Use these prompts in **VS Code Copilot Chat** to get interactive help with setup, usage, and troubleshooting.

---

## 🚀 **Getting Started Prompts**

### **Prompt 1: Help me install and setup Copilot Chat Exporter**

```
I want to set up the Copilot Chat History Exporter on my Windows machine. 
Can you guide me through the installation process step-by-step? 
I need help with:
1. Checking if Python is installed
2. Cloning the GitHub repository
3. Running the interactive setup
4. Setting up Windows Task Scheduler

Please explain what each step does and what to expect.
```

### **Prompt 2: I just cloned the repo, what do I do next?**

```
I've cloned https://github.com/nchandik/copilot-chat-exporter.git to my computer.
What are the next steps to get the Copilot Chat exporter working?
I need clear instructions I can follow, including how to test if it works.
```

### **Prompt 3: Check if my computer is ready for this tool**

```
Help me verify my computer has everything needed for Copilot Chat History Exporter:
- How do I check if Python 3.7+ is installed?
- How do I confirm VS Code has Copilot Chat enabled?
- What Windows version do I need?
- Is there anything else I need to check?
```

---

## ⚙️ **Setup & Configuration Prompts**

### **Prompt 4: Walk me through the setup wizard**

```
I'm about to run "python export_copilot_history.py --setup"
Can you explain what each question is asking and help me decide:
1. Where should I save my chat history files?
2. What time should I set for daily exports? (considering IST timezone)
3. Do timezone choices affect when exports run?
```

### **Prompt 5: Help me choose an output directory**

```
I need to choose where to save my exported Copilot chats.
Here are my options:
- C:\Users\YourName\Documents\Copilot-History (default)
- My cloud storage folder (OneDrive/Google Drive)
- An external drive

Which option is best and why? What are the pros and cons?
```

### **Prompt 6: Help me set the export time**

```
I work in IST timezone and want to export my chat history daily.
What time should I set the export for?
- I'm usually at my desk until 6:00 PM (18:00)
- I want the export to happen automatically
- What happens if I'm not at my desk at that time?

Give me your recommendation with reasons.
```

### **Prompt 7: I messed up the setup, how do I fix it?**

```
I ran the setup but made a mistake in my configuration.
Can I change it? What's the command to re-run setup?
Where is my configuration file saved?
Can I manually edit the config file if needed?
```

---

## 🔧 **Troubleshooting Prompts**

### **Prompt 8: Python says "command not found"**

```
When I try to run "python export_copilot_history.py --setup"
I get an error: "'python' is not recognized as an internal or external command"

What does this mean and how do I fix it?
```

### **Prompt 9: The script can't find my chat sessions**

```
I ran the exporter but got this error:
"❌ Error finding session files"

Why is this happening? How do I fix it?
What does "session files" mean?
```

### **Prompt 10: The scheduled task isn't running automatically**

```
I set up the Windows Task Scheduler for daily exports, but it's not running.
How do I:
1. Check if the task was created correctly?
2. Verify it will run at the right time?
3. Manually test if it works?
4. Fix it if there's a problem?
```

### **Prompt 11: Permission denied errors on Windows**

```
I'm getting "Access is denied" errors when trying to run the script.
Why is this happening?
What should I do differently?
Do I need to run as Administrator? How?
```

---

## 📖 **Usage & Features Prompts**

### **Prompt 12: What's the difference between JSON and Markdown outputs?**

```
The exporter creates both JSON and Markdown files.
Can you explain:
- What is each format good for?
- When should I use JSON vs Markdown?
- Can I open these files in any program?
- What information do they contain?
```

### **Prompt 13: How do I export past chat history?**

```
I want to export chat history from a previous day, not just today.
What command should I use?
How far back can I go?
What if I don't have session files from that day?
```

### **Prompt 14: I want to export to a different folder sometimes**

```
How do I temporarily export to a different location without changing my configuration?
Do I lose my original settings?
What's the command to do this?
```

### **Prompt 15: How do I back up my exported files?**

```
I'm storing my exported Copilot chats and want to back them up.
What are the best strategies for:
- Cloud storage integration?
- Archiving old files?
- Keeping multiple copies?
- Organizing files by date?
```

---

## 🔐 **Privacy & Security Prompts**

### **Prompt 16: Is it safe to export my chat history?**

```
I'm concerned about privacy and security.
Can you explain:
- What information is exported in the files?
- Where are the files stored?
- Is my private information included?
- What should I be careful about when sharing these files?
```

### **Prompt 17: How do I keep my exported chats private?**

```
I want to export my Copilot chat history but keep it private.
What options do I have for:
- Encrypting the files?
- Restricting access?
- Cloud storage security?
- Secure deletion of old files?
```

---

## 📊 **Advanced Prompts**

### **Prompt 18: Can I use this across multiple machines?**

```
I have multiple computers (work laptop, personal computer, etc).
Can I:
- Run the exporter on all of them?
- Use the same configuration across machines?
- Consolidate exports from multiple machines?
- Sync my chats across computers?
```

### **Prompt 19: What if I'm working in a team?**

```
My whole team wants to use the Copilot Chat History Exporter.
How do we:
- Each set up our own configuration?
- Store chats in a shared location?
- Manage different timezones (IST and US)?
- Avoid conflicts or overlapping exports?
```

### **Prompt 20: Automate with PowerShell instead of batch**

```
I prefer PowerShell over batch scripts.
Can you:
- Explain what the batch file (schedule_daily.bat) does?
- Show me how to create a PowerShell equivalent?
- Help me schedule it with PowerShell instead?
- Make sure it has the same functionality?
```

---

## 🆘 **When Something Goes Wrong**

### **Prompt 21: Something's broken, help me diagnose**

```
My Copilot Chat Exporter stopped working.
Here's what I see when I run it:
[paste the error message here]

Can you help me:
1. Understand what went wrong?
2. Find the root cause?
3. Fix the problem?
4. Test if it works now?
```

### **Prompt 22: I want to completely reset and start over**

```
I want to uninstall and completely reset the Copilot Chat Exporter.
Please guide me through:
- Where to find and delete config files?
- How to remove the scheduled task?
- How to clean up my exported files?
- How to start fresh from scratch?
```

---

## 💡 **How to Use These Prompts**

### **Option 1: Copy & Paste in Copilot Chat**

1. Open VS Code with Copilot Chat (Ctrl+L or click chat icon)
2. Copy one of the prompts above
3. Paste it into the chat
4. Follow the guidance Copilot provides

### **Option 2: Customize for Your Situation**

The prompts are templates! Feel free to modify them with:
- Your actual error messages
- Your specific setup (IST vs EST timezone)
- Your company policies or requirements
- Your specific questions

### **Option 3: Ask Follow-up Questions**

After Copilot responds, you can ask:
- "Can you give me an example?"
- "Explain this simpler"
- "What if I..."
- "How do I test this?"

---

## 📝 **Tips for Best Results**

### **Be Specific**
Instead of: "Why isn't it working?"  
Better: "When I run `python export_copilot_history.py`, I get error: `[specific error]`"

### **Include Error Messages**
Copy the exact error text from your terminal/console.

### **Describe Your Setup**
- Windows version
- Python version
- Where you cloned the repo
- What step you're stuck on

### **Ask for Next Steps**
Always ask: "What should I try next if this doesn't work?"

---

## 🎯 **Quick Navigation**

| Topic | Prompt # |
|-------|---------|
| Getting Started | 1, 2, 3 |
| Setup & Config | 4, 5, 6, 7 |
| Troubleshooting | 8, 9, 10, 11 |
| Usage | 12, 13, 14, 15 |
| Privacy | 16, 17 |
| Advanced | 18, 19, 20 |
| Emergency | 21, 22 |

---

## 🚀 **Start Here**

If you're new to the Copilot Chat Exporter:

1. **First:** Use **Prompt 1** → "Help me install and setup..."
2. **Then:** Use **Prompt 4** → "Walk me through the setup wizard..."
3. **Finally:** Use **Prompt 12** → "What's the difference between JSON and Markdown..."

Happy chatting with Copilot! 💬

---

**Need more help?**
- Check the main [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Visit [GitHub Repository](https://github.com/nchandik/copilot-chat-exporter)
- Review [README.md](README.md) for features and usage
