@echo off
setlocal
cd /d "%~dp0"
title Estudio de Animacao Local - M0
echo ============================================================
echo  ESTUDIO DE ANIMACAO LOCAL - M0
echo ============================================================
echo.
echo  A interface grafica entra a partir do M2.
echo  Neste marco, use os comandos abaixo nesta pasta:
echo.
echo  1) Perfil de hardware:
echo     py -3.12 descoberta\hardware.py --salvar
echo.
echo  2) Descobrir programas (somente leitura):
echo     py -3.12 descoberta\programas.py --max-seconds 180
echo.
echo  3) Inventariar modelos do ComfyUI:
echo     py -3.12 descoberta\modelos.py --comfyui "D:\Comfy\ComfyUI" --salvar
echo.
echo  4) Testar a GPU:
echo     "D:\Comfy\ComfyUI\venv\Scripts\python.exe" descoberta\teste_gpu.py --salvar
echo.
echo  5) Rodar os testes da descoberta:
echo     py -3.12 -m unittest discover -s tests -v
echo.
echo  Docs: docs\progresso.md, docs\decisoes.md, docs\licencas.md
echo ============================================================
pause
