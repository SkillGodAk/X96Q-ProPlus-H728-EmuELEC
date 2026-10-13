# X96Q Pro+ H728-EmuELEC 4.8

[繁體中文](README.md) · [简体中文](README.zh-CN.md) · [English](README.en.md)

專為 **X96Q Pro+（H728）** 整合的 EmuELEC 4.8 雙版本純淨映像。採用 Crystal 主題、繁體中文預設與自動建立的 EEROMS 遊戲分區。

> **相容性提醒**：本專案主要針對作者實際使用的 X96Q Pro+ H728 盒子。即使其他盒子也標示 H728，仍可能採用不同的裝置樹、遙控器、紅外線及供電方式；沒有經過測試的型號，**不保證相容**。刷寫 SD 前請備份重要資料。

## 先選擇版本

| 功能 | **NoRoot：純 EmuELEC** | **Root：Android + EmuELEC** |
| --- | --- | --- |
| 開機預設系統 | **EmuELEC** | **原機 Android** |
| 是否需要 Android ROOT | **不需要** | **需要原廠 Android 可授權 `su`** |
| 原廠遙控器關機後喚醒 | **支援，喚醒進 EmuELEC** | **支援，喚醒進 Android** |
| GameSwitch APK | 不需要 | **需要**；在 Android 切換至 EE |
| 首次建立 EEROMS FAT32 遊戲分區 | 支援 | 進入 EE 後支援 |
| Crystal 主題、繁中、核心與手把設定 | 支援 | 支援 |

**Root 特別注意**：此版只針對**原款 X96Q Pro+ H728、原廠 Android 環境和原廠遙控器**進行相容性設計與測試。Root 是指 Android 端已有可用的 ROOT／`su` 權限，**不是替你的盒子取得 ROOT**。其他 H728 盒子是否能正常使用 APK、冷開機、關機或紅外線喚醒，目前沒有足夠實測可保證。

**NoRoot 一樣支援原廠遙控器關機後喚醒**，但喚醒目標是 **EmuELEC**，不是 Android。兩版在原機上的喚醒目標不同，不代表 NoRoot 沒有遙控器功能。

## 相較於一般 EmuELEC 4.8，本專案針對 H728 整合

- H728／X96Q Pro+ 的開機鏈、裝置樹與硬體相容調整，包含 AXP323 冷開機初始化。
- 盒子原廠遙控器的關機與紅外線喚醒路徑；NoRoot 返回 EE、Root 返回 Android。
- 首次啟動自動建立／延展 FAT32 `EEROMS` 遊戲分區，適應不同容量的 SD；後續啟動不重新格式化。
- Crystal 預設主題、繁體中文介面和遊戲系統資料夾；整合 43 個工廠核心檔案（實際可玩的遊戲與 BIOS 需自行準備）。
- Root 版的 Android／EE 切換及正常 EE 重新啟動路由。

這些是針對此硬體的整合差異；並非聲稱所有 EmuELEC 4.8 原生功能都是本專案首次發明。

## 下載

請從 [**GitHub Releases**](../../releases) 下載**最新正式版**，解壓後取得 IMG：

| 檔案 | 內容 |
| --- | --- |
| `X96Q pro+_H728_EmuELEC_4.8_NoRoot.7z` | 純 EE，開機與遙控喚醒都進 EE |
| `X96Q pro+_H728_EmuELEC_4.8_Root.7z` | Android 優先雙系統；遙控喚醒回 Android |
| `H728-GameSwitch.apk` | **僅 Root 版**在 Android 端切換到 EE 使用 |

上述檔名是自行上傳的正式版附件，不包含 GitHub 平台自動提供的原始碼歸檔。正式版一律以該 Release 的 SHA256／驗證說明為準。

## 安裝步驟

1. 先備份 SD 卡。下載對應的 `.7z`，使用 7-Zip 完整解壓出 `.img`，**不要把 7z 直接寫進卡片**。
2. 使用 [balenaEtcher](https://etcher.balena.io/) 選擇 IMG、正確的 **SD 卡**，執行 Flash 並等待驗證結束。選錯磁碟會造成資料遺失。
3. 斷電後插入 SD，再接電開機。**NoRoot** 會進 EmuELEC；**Root** 初次仍會進原機 Android，須在具備 ROOT／`su` 權限的 Android 安裝並開啟 GameSwitch APK，授權後切換到 EE。
4. 第一次進 EE 時，讓自動設定及 FAT32 `EEROMS` 分區建立流程正常完成。**不要在擴容／安裝核心途中斷電、拔卡或反覆按重啟**。
5. 後續 SD 卡擴容完成後，正常重啟不應再格式化已存在的 `EEROMS`。

**注意**：Android 本身保留在盒子的原儲存裝置，這兩份 IMG 是供 SD 卡燒錄使用；不要把 IMG 寫入 eMMC 或電視盒內建 Android 分區。

## 如何新增遊戲

系統完成第一次初始化後，把 SD 接回電腦，開啟 FAT32 的 **`EEROMS`** 遊戲分區。依系統將你合法持有的遊戲檔放到對應目錄，例如 `roms/nes`、`roms/snes`、`roms/psx`（以卡上實際建立的目錄名稱為準）；部分模擬器另外需要 BIOS，依平台放入對應 `bios` 位置。安全退出 SD，回到 EE 後重新整理遊戲清單。別覆寫原有的設定、遊戲存檔或 BIOS。

## 已知限制

- **僅有 X96Q Pro+ H728 原機組合的驗證依據**；其他標示 H728 的盒子未驗證。
- Root 的 APK 需要 Android 可用的 ROOT／`su`；不會自行 ROOT 裝置，也不附任何商業遊戲 ROM 或 BIOS。
- 按照不同 SD 卡容量，首次 EEROMS 擴容時間可能不同。勿中斷；若有錯誤，請保留畫面和日誌回報。
- 本專案不是 EmuELEC／裝置品牌官方發行版；商標與上游成果歸各自權利人所有。

## 支持作者

如果這個專案對你有幫助，歡迎自願支持獨立開發者。

**海外贊助：** [Buy Me a Coffee](https://buymeacoffee.com/SkillGodAK)

[![Buy Me a Coffee](https://raw.githubusercontent.com/SkillGodAk/DRO/main/assets/donate-buymeacoffee.svg)](https://buymeacoffee.com/SkillGodAK)

**銀行贊助：**

![銀行贊助 QR Code](https://raw.githubusercontent.com/SkillGodAk/DRO/main/assets/donate-bank.jpg)

**微信收款：**

![微信贊助 QR Code](https://raw.githubusercontent.com/SkillGodAk/DRO/main/assets/donate-wechat.jpg)

---

本專案為非官方第三方整合；不提供遊戲 ROM、BIOS 或原廠 Android 映像。包含開源元件的發行與原始碼取得資訊請參閱 [SOURCE-AND-LICENSES.md](SOURCE-AND-LICENSES.md)。
