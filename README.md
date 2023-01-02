<img src="public/logo/logo-no-background.png" width=90% height=90%>

The repository of the graduation project ***"AI assistant for video creators"*** in [MADE](https://data.vk.company/) [2022].  

## Description
The following is the general architecture of the project:

## 
```bash
cd app
python inference.py casum --source input/12345/apple.mp4 --save-path ../output/12345/apple.mp4 --final-frame-length 27 --device cuda
python cover_gen.py smart --source ../_videos/1.png --save-path ../output/1_text.png --text "TRAVEL BLOG" --position "left-top" --font-path fonts/CenturySB-Bold.ttf --font-size 60 --font-color white --stroke-color black --stroke-width 5
```