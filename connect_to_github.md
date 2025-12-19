# Подключение к GitHub - Пошаговая инструкция

## Ваши текущие настройки Git:
- **Имя пользователя**: PaladiniSHE
- **Email**: alvshutov.72@gmail.com

## Шаг 1: Создайте репозиторий на GitHub

### Вариант A: Через веб-интерфейс GitHub

1. Откройте браузер и перейдите на https://github.com
2. Войдите в свой аккаунт (или создайте новый)
3. Нажмите кнопку **"+"** в правом верхнем углу → **"New repository"**
4. Заполните форму:
   - **Repository name**: `vols-gis` (или другое имя)
   - **Description**: `Vols GIS - Система учета ВОЛС`
   - **Visibility**: Public или Private (на ваше усмотрение)
   - ⚠️ **ВАЖНО**: НЕ ставьте галочки на:
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
   (эти файлы уже есть в проекте)
5. Нажмите **"Create repository"**

### Вариант B: Через GitHub CLI (если установлен)

```bash
gh repo create vols-gis --public --source=. --remote=origin --push
```

## Шаг 2: Определите ваш GitHub username

После создания репозитория, URL будет выглядеть так:
- `https://github.com/ВАШ_USERNAME/vols-gis.git`

Где `ВАШ_USERNAME` - это ваш логин на GitHub.

## Шаг 3: Добавьте удаленный репозиторий

Замените `ВАШ_USERNAME` на ваш реальный username GitHub:

```bash
cd "C:\Users\ShutovAV\OneDrive - cpjj\Desktop\projects\Vols BD"
git remote add origin https://github.com/ВАШ_USERNAME/vols-gis.git
```

Например, если ваш username `PaladiniSHE`:
```bash
git remote add origin https://github.com/PaladiniSHE/vols-gis.git
```

## Шаг 4: Проверьте подключение

```bash
git remote -v
```

Должно показать:
```
origin  https://github.com/ВАШ_USERNAME/vols-gis.git (fetch)
origin  https://github.com/ВАШ_USERNAME/vols-gis.git (push)
```

## Шаг 5: Отправьте код на GitHub

```bash
git push -u origin main
```

При первом push GitHub может запросить авторизацию:
- Если используете HTTPS, потребуется Personal Access Token (PAT)
- Если используете SSH, нужен SSH ключ

### Настройка Personal Access Token (для HTTPS):

1. Перейдите на https://github.com/settings/tokens
2. Нажмите **"Generate new token"** → **"Generate new token (classic)"**
3. Задайте имя токена (например, "Vols GIS")
4. Выберите срок действия (например, "No expiration")
5. Выберите права доступа: **repo** (полный доступ к репозиториям)
6. Нажмите **"Generate token"**
7. **Скопируйте токен** (он показывается только один раз!)
8. При выполнении `git push` используйте токен вместо пароля:
   - Username: ваш GitHub username
   - Password: вставьте скопированный токен

### Альтернатива: Использование SSH (рекомендуется)

1. Создайте SSH ключ (если еще нет):
```bash
ssh-keygen -t ed25519 -C "alvshutov.72@gmail.com"
```

2. Добавьте публичный ключ на GitHub:
   - Скопируйте содержимое `~/.ssh/id_ed25519.pub`
   - Перейдите на https://github.com/settings/keys
   - Нажмите **"New SSH key"**
   - Вставьте ключ и сохраните

3. Используйте SSH URL вместо HTTPS:
```bash
git remote set-url origin git@github.com:ВАШ_USERNAME/vols-gis.git
```

## Шаг 6: Проверьте результат

Откройте ваш репозиторий на GitHub:
```
https://github.com/ВАШ_USERNAME/vols-gis
```

Все файлы должны быть там!

## Ежедневная работа

После настройки, для отправки изменений:

```bash
git add .
git commit -m "Описание изменений"
git push origin main
```

Для получения изменений с GitHub:

```bash
git pull origin main
```

## Решение проблем

### Ошибка: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/ВАШ_USERNAME/vols-gis.git
```

### Ошибка: "Authentication failed"
- Проверьте правильность Personal Access Token
- Или настройте SSH ключ

### Ошибка: "Repository not found"
- Проверьте правильность username в URL
- Убедитесь, что репозиторий создан на GitHub

