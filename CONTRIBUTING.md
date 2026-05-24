# Guide de Contribution

Merci de votre intérêt pour contribuer à Agent IA Autonome!

## 🎯 Normes de Contribution

### 1. Fork et Clone
```bash
git clone https://github.com/your-username/agent-ia-otonome.git
cd agent-ia-otonome
```

### 2. Créer une branche
```bash
git checkout -b feature/description-de-la-feature
# ou
git checkout -b bugfix/description-du-bug
```

### 3. Développer et tester
```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer les tests
pytest tests/ -v

# Vérifier le formatage du code
flake8 .
```

### 4. Commit et Push
```bash
git add .
git commit -m "feat: description claire de la modification"
git push origin feature/description
```

### 5. Créer une Pull Request
- Fournir une description claire
- Référencer les issues liées
- S'assurer que les tests passent

## 📋 Types de Contributions

### Issues
- 🐛 Bug reports
- ✨ Feature requests
- 📚 Documentation
- ❓ Questions

### Pull Requests
- Code improvements
- Bug fixes
- Documentation
- Tests

## 🔍 Standards de Code

### Python
- Suivre PEP 8
- Type hints recommandées
- Docstrings pour les fonctions
- Tests unitaires pour les nouvelles features

### Commits
```bash
feat: nouvelle feature
fix: correction de bug
docs: documentation
style: formatage
refactor: refactorisation
test: tests
chore: maintenance
```

## ✅ Checklist PR

- [ ] Code testé localement
- [ ] Tests unitaires passent
- [ ] Code passe flake8
- [ ] Documentation mise à jour
- [ ] Commits bien documentés
- [ ] Pas de fichiers sensibles commités

## 🏆 Reconnaissance

Les contributeurs seront mentionnés dans:
- README.md
- CONTRIBUTORS.md (à créer)
- Releases notes

## 📞 Questions?

Créez une issue ou contactez les mainteneurs.

---

Merci de vos contributions! 🚀
