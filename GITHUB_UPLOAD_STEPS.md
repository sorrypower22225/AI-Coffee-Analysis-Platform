# GitHub 上傳步驟

## 1. 解壓縮資料夾

把 `AI_Coffee_GitHub_Ready.zip` 解壓縮到桌面。

## 2. 開啟 PowerShell

進入專案資料夾：

```powershell
cd C:\Users\115A\Desktop\AI_Coffee_GitHub_Ready
```

## 3. 初始化 Git

如果這個資料夾還沒有 Git：

```powershell
git init
```

## 4. 加入遠端 GitHub Repository

請把網址改成你自己的 GitHub 倉庫網址：

```powershell
git remote add origin https://github.com/你的帳號/你的專案名稱.git
```

如果已經有 remote，可以改用：

```powershell
git remote set-url origin https://github.com/你的帳號/你的專案名稱.git
```

## 5. 上傳

```powershell
git status
git add .
git commit -m "整理咖啡 AI 商業分析專案"
git branch -M main
git push -u origin main
```

## 注意

完整清洗資料 `Coffee_Shop_Enterprise_Features_Corrected.csv` 約 263MB，超過 GitHub 一般單檔 100MB 限制，不建議直接上傳。
