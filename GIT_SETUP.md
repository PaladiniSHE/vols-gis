# Настройка Git репозитория для Vols GIS

## Текущий статус

✅ Git репозиторий инициализирован
✅ .gitignore файл создан
✅ Первый коммит выполнен
✅ README.md добавлен

## Следующие шаги для синхронизации с удаленным репозиторием

### 1. Создайте репозиторий на GitHub/GitLab/Bitbucket

1. Перейдите на GitHub (https://github.com) или другой Git-хостинг
2. Создайте новый репозиторий (например, `vols-gis`)
3. **НЕ** инициализируйте его с README, .gitignore или лицензией (они уже есть)

### 2. Добавьте удаленный репозиторий

```bash
cd "C:\Users\ShutovAV\OneDrive - cpjj\Desktop\projects\Vols BD"
git remote add origin https://github.com/ВАШ_USERNAME/vols-gis.git
```

Или для SSH:
```bash
git remote add origin git@github.com:ВАШ_USERNAME/vols-gis.git
```

### 3. Переименуйте ветку в main (если нужно)

```bash
git branch -M main
```

### 4. Отправьте код в удаленный репозиторий

```bash
git push -u origin main
```

### 5. Настройте автоматическую синхронизацию

#### Вариант A: Ручная синхронизация

```bash
# Получить изменения
git pull origin main

# Отправить изменения
git push origin main
```

#### Вариант B: Настройка автоматической синхронизации через OneDrive

Если проект находится в OneDrive, изменения будут автоматически синхронизироваться между устройствами. Однако для работы с Git рекомендуется использовать удаленный репозиторий (GitHub/GitLab).

### 6. Ежедневная работа с Git

```bash
# Проверить статус
git status

# Добавить изменения
git add .

# Создать коммит
git commit -m "Описание изменений"

# Отправить на сервер
git push origin main

# Получить изменения с сервера
git pull origin main
```

## Полезные команды

```bash
# Просмотр истории коммитов
git log --oneline

# Просмотр изменений
git diff

# Создание новой ветки
git checkout -b feature/new-feature

# Переключение между ветками
git checkout main

# Слияние веток
git merge feature/new-feature
```

## Настройка Git (если еще не настроено)

```bash
git config --global user.name "Ваше Имя"
git config --global user.email "ваш@email.com"
```

## Решение проблем

### Если нужно обновить удаленный URL:
```bash
git remote set-url origin НОВЫЙ_URL
```

### Если нужно проверить текущий удаленный репозиторий:
```bash
git remote -v
```

### Если нужно удалить удаленный репозиторий:
```bash
git remote remove origin
```


