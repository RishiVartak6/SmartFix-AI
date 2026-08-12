const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 1050,
    minHeight: 700,
    title: 'SmartFix AI — Intelligent Windows Troubleshooting System',
    frame: true,
    titleBarStyle: 'default',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false
    },
    icon: path.join(__dirname, 'icon.png'),
    backgroundColor: '#0B0F19'
  });

  // Remove native default menu bar for sleek clean Windows app look
  win.setMenuBarVisibility(false);

  const startUrl = process.env.ELECTRON_START_URL || 'http://localhost:5173';
  win.loadURL(startUrl);
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
