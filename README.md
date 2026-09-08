# VV x Stratos — The Wall

One shared page for the whole team. One card per person. You edit only your own card.

Live page: https://mody-sahariar1.github.io/vv-wall/

## Join the wall: one paste, then talk

Paste ONE of these into your terminal. It copies the wall to your Desktop and opens Claude Code inside it.

Mac (Terminal):

    gh repo clone mody-sahariar1/vv-wall ~/Desktop/vv-wall && cd ~/Desktop/vv-wall && claude

Windows (PowerShell):

    gh repo clone mody-sahariar1/vv-wall $HOME\Desktop\vv-wall; cd $HOME\Desktop\vv-wall; claude

Claude Code asks "do you trust this folder?" once. Say yes.

Already have the folder? Just: `cd ~/Desktop/vv-wall` then `claude`.

Then say, in plain English:

    Claim my card on the wall. Find the block with my GitHub username between the START and END markers in index.html, put my name and my role, pick a colour I like, and publish it.

Claude Code edits your block, saves, and pushes it. About a minute later the live page shows your card.

Want more? Say it: "add my photo", "make the background green", "add a line about my programme", "add a link to our website". Then: "publish it".

## Rules

1. Edit only inside your own START and END markers. Claude Code knows this, remind it if it wanders.
   Keep everything for your card inside your block, including any styling (use style attributes or a
   <style> tag inside your own section). Never edit the shared <style> block at the top of the page:
   that is the one place two people's changes collide.
2. Nobody types a git command. Claude Code handles pull, commit and push. If it says the push was rejected, say: "someone else pushed, pull their work and push mine again".
3. If the page breaks, that is fine. We fix it live.

## If you do not have a card

Tell Claude Code: "add a card for me at the end of the wall, using my GitHub username, and publish it".
