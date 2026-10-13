.class public final Lcom/skillgod/h728gameswitch/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.java"

.method public constructor <init>()V
    .locals 0
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V
    return-void
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .locals 7

    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    const-string v0, "正在進入遊戲系統…"
    const/4 v1, 0x1
    invoke-static {p0, v0, v1}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    move-result-object v0
    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    const/4 v0, 0x5
    new-array v0, v0, [Ljava/lang/String;

    const/4 v1, 0x0
    const-string v2, "/system/xbin/su"
    aput-object v2, v0, v1

    const/4 v1, 0x1
    const-string v2, "0"
    aput-object v2, v0, v1

    const/4 v1, 0x2
    const-string v2, "/system/bin/sh"
    aput-object v2, v0, v1

    const/4 v1, 0x3
    const-string v2, "-c"
    aput-object v2, v0, v1

    const/4 v1, 0x4
    const-string v2, "LOG=/data/local/tmp/h728_game_switch.log; echo \"=== $(date) ===\" > \"$LOG\"; found=0; for x in /sys/class/block/mmcblk*; do t=$(cat \"$x/device/type\" 2>/dev/null); r=$(cat \"$x/removable\" 2>/dev/null); [ \"$t\" = \"SD\" ] || [ \"$r\" = \"1\" ] || continue; n=${x##*/}; d=/dev/block/$n; [ -b \"$d\" ] || d=/dev/$n; [ -b \"$d\" ] || continue; cur=$(dd if=\"$d\" bs=1 skip=8196 count=8 2>/dev/null); echo \"device=$d type=$t removable=$r magic=$cur\" >> \"$LOG\"; if [ \"$cur\" = \"eGON.OFF\" ]; then printf 'eGON.BT0' | dd of=\"$d\" bs=1 seek=8196 conv=notrunc 2>>\"$LOG\" || exit 11; elif [ \"$cur\" != \"eGON.BT0\" ]; then continue; fi; sync; new=$(dd if=\"$d\" bs=1 skip=8196 count=8 2>/dev/null); echo \"verify=$new\" >> \"$LOG\"; [ \"$new\" = \"eGON.BT0\" ] || exit 12; found=1; break; done; [ \"$found\" = \"1\" ] || exit 13; reboot"
    aput-object v2, v0, v1

    :try_start_0
    new-instance v1, Ljava/lang/ProcessBuilder;
    invoke-direct {v1, v0}, Ljava/lang/ProcessBuilder;-><init>([Ljava/lang/String;)V

    const/4 v2, 0x1
    invoke-virtual {v1, v2}, Ljava/lang/ProcessBuilder;->redirectErrorStream(Z)Ljava/lang/ProcessBuilder;
    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/ProcessBuilder;->start()Ljava/lang/Process;
    :try_end_0
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_0

    goto :done

    :catch_0
    move-exception v0
    const-string v1, "無法取得 root 權限或啟動切換程序"
    const/4 v2, 0x1
    invoke-static {p0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    move-result-object v1
    invoke-virtual {v1}, Landroid/widget/Toast;->show()V

    :done
    invoke-virtual {p0}, Landroid/app/Activity;->finish()V
    return-void
.end method
