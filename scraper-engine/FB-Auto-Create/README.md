# FB Auto Create (Node.js + Python)

**⚠️ Warning:** Using this script will most likely (90% chance) get the created Facebook account suspended.  
Use strictly for **educational/testing purposes** only. Any illegal or abusive usage can lead to legal consequences.

---

## 📦 Installation

```bash
git clone https://github.com/smfahimbd/FB-Auto-Create.git
cd FB-Auto-Create
npm install
pip install -r requirements.txt
```

---

## ▶ Usage

### **Node.js Version**
```bash
node index.js
```

### **Python Version**
```bash
python main.py
```

---

## 🐳 Run with Docker

Build the image:
```bash
docker build -t FB-Auto-Create .
```

Run Node.js script:
```bash
docker run --rm FB-Auto-Create node index.js
```

Run Python script:
```bash
docker run --rm FB-Auto-Create python main.py
```

---

## 📁 File Structure

```
FB-Auto-Create/
├── Dockerfile          # Docker support
├── README.md           # README.md support
├── index.js            # Node.js version
├── main.py             # Python version
├── package.json        # Node.js dependencies
└── requirements.txt    # Python dependencies
```

---

## ⚠ Disclaimer
- This project is for **educational/testing purposes only**.
- Violating Facebook's terms of service may result in your account being suspended or banned.
- Use at your own risk.

## 📄 License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.

---
## Author

Made with ❤️ by [@smfahimcp](https://github.com/smfahimcp)
