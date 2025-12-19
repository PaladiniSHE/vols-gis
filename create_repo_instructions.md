# Инструкция по созданию репозитория на GitHub

## Быстрый способ

1. **Откройте в браузере:** https://github.com/new

2. **Войдите в свой аккаунт GitHub** (если еще не вошли)

3. **Заполните форму создания репозитория:**
   - **Repository name:** `vols-gis`
   - **Description:** `Vols GIS - Система учета ВОЛС` (опционально)
   - **Visibility:** 
     - ✅ **Public** - репозиторий будет виден всем
     - ✅ **Private** - репозиторий будет доступен только вам
   - ⚠️ **ВАЖНО:** НЕ ставьте галочки на:
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
   
   (Эти файлы уже есть в вашем локальном проекте)

4. **Нажмите кнопку "Create repository"**

5. **После создания репозитория вернитесь в терминал и выполните:**
   ```bash
   cd "C:\Users\ShutovAV\OneDrive - cpjj\Desktop\projects\Vols BD"
   git push -u origin main
   ```

## Альтернативный способ: GitHub CLI

Если у вас установлен GitHub CLI (`gh`):

```bash
# Авторизация (если еще не авторизованы)
gh auth login

# Создание репозитория и отправка кода одной командой
gh repo create vols-gis --public --source=. --remote=origin --push
```

Или для приватного репозитория:
```bash
gh repo create vols-gis --private --source=. --remote=origin --push
```

## Проверка после создания

После создания репозитория проверьте, что он доступен:
- URL: `https://github.com/PaladiniSHE/vols-gis` (или ваш username)

## Если username отличается

Если ваш GitHub username отличается от `PaladiniSHE`, обновите remote перед push:

```bash
git remote set-url origin https://github.com/ВАШ_USERNAME/vols-gis.git
git push -u origin main
```

## Авторизация при push

При первом `git push` GitHub запросит авторизацию:

- **Username:** ваш GitHub username
- **Password:** используйте **Personal Access Token** (не пароль!)

### Создание Personal Access Token:

1. Перейдите на: https://github.com/settings/tokens
2. Нажмите **"Generate new token"** → **"Generate new token (classic)"**
3. Задайте имя: `Vols GIS`
4. Выберите срок: `No expiration` (или нужный вам)
5. Выберите права: **repo** (полный доступ к репозиториям)
6. Нажмите **"Generate token"**
7. **Скопируйте токен** (показывается только один раз!)
8. Используйте его как пароль при `git push`

