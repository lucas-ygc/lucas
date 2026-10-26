#include "ptzpanel.h"
#include <QComboBox>
#include <QGridLayout>
#include <QGroupBox>
#include <QHideEvent>
#include <QLabel>
#include <QPushButton>
#include <QSpinBox>
#include <QDoubleSpinBox>
#include <QTimer>
#include <QUuid>
#include <QVBoxLayout>

PtzPanel::PtzPanel(QWidget *parent)
: QWidget(parent)
{
    auto *outer = new QVBoxLayout(this);
    outer->setContentsMargins(0, 0, 0, 0);
    auto *group = new QGroupBox("云台控制", this);
    outer->addWidget(group);
    auto *grid = new QGridLayout(group);
    const QString arrows[] = {"←", "→", "↑", "↓"};
    const int rows[] = {1, 1, 0, 2}, cols[] = {0, 2, 1, 1};
    for (unsigned i = 0; i < 4; ++i) {
        directions[i] = new QPushButton(arrows[i], group);
        directions[i]->setMinimumHeight(36);
        grid->addWidget(directions[i], rows[i], cols[i]);
        unsigned axis = i < 2 ? 0 : 1;
        bool inc = (i == 0 || i == 3);
        connect(directions[i], &QPushButton::pressed, this, [this, axis, inc] { begin(axis, inc); });
        connect(directions[i], &QPushButton::released, this, [this, axis] { release(axis); });
    }
    auto *stop = new QPushButton("停止", group);
    grid->addWidget(stop, 1, 1);
    connect(stop, &QPushButton::clicked, this, [this] {
        release(0);
        release(1);
        emit command("ptz_stop", {{"axis", "both"}});
    });
    speed = new QComboBox(group);
    for (int i = 1; i <= 5; ++i)
        speed->addItem(QString("%1 档（%2 步/秒）").arg(i).arg(i * 100), i);
    grid->addWidget(speed, 3, 0, 1, 3);
    home = new QPushButton("校准并回中", group);
    center = new QPushButton("回中", group);
    grid->addWidget(home, 4, 0, 1, 2);
    grid->addWidget(center, 4, 2);
    connect(home, &QPushButton::clicked, this, [this] {
        release(0);
        release(1);
        emit command("ptz_home", {{"axis", "both"}, {"level", speed->currentData().toInt()}});
    });
    connect(center, &QPushButton::clicked, this, [this] {
        release(0);
        release(1);
        emit command("ptz_center", {{"axis", "both"}, {"level", speed->currentData().toInt()}});
    });
    for (unsigned i = 0; i < 2; ++i) {
        grid->addWidget(new QLabel(i ? "垂直目标" : "水平目标", group), 5 + i, 0);
        target[i] = new QSpinBox(group);
        target[i]->setRange(0, 0);
        grid->addWidget(target[i], 5 + i, 1);
        move[i] = new QPushButton("移动", group);
        grid->addWidget(move[i], 5 + i, 2);
        connect(move[i], &QPushButton::clicked, this, [this, i] {
            release(i);
            emit command("ptz_move_to", {{"axis", i ? "v" : "h"}, {"position", target[i]->value()}, {"level", speed->currentData().toInt()}});
        });
    }
    status = new QLabel("等待设备云台状态", group);
    status->setWordWrap(true);
    error = new QLabel(group);
    error->setWordWrap(true);
    grid->addWidget(status, 7, 0, 1, 3);
    grid->addWidget(error, 8, 0, 1, 3);
    auto *ranges = new QGroupBox("行程配置", this);
    outer->addWidget(ranges);
    auto *rangeGrid = new QGridLayout(ranges);
    for (unsigned i = 0; i < 2; ++i) {
        rangeGrid->addWidget(new QLabel(i ? "垂直最大角度" : "水平最大角度", ranges), i, 0);
        maxAngle[i] = new QDoubleSpinBox(ranges);
        maxAngle[i]->setObjectName(i ? "ptzVerticalAngle" : "ptzHorizontalAngle");
        maxAngle[i]->setDecimals(2);
        maxAngle[i]->setRange(0.1, 360.0);
        maxAngle[i]->setSuffix("°");
        maxAngle[i]->setEnabled(false);
        rangeGrid->addWidget(maxAngle[i], i, 1);
    }
    auto *advanced = new QGroupBox("高级：归零寻找行程（半步）", ranges);
    advanced->setCheckable(true);
    advanced->setChecked(false);
    advanced->setToolTip("寻找机械零点的行程，独立于正常运动范围；不能随最大角度自动缩小。");
    auto *advancedGrid = new QGridLayout(advanced);
    for (unsigned i = 0; i < 2; ++i) {
        advancedGrid->addWidget(new QLabel(i ? "垂直" : "水平", advanced), i, 0);
        seekSteps[i] = new QSpinBox(advanced);
        seekSteps[i]->setRange(1, 60000);
        seekSteps[i]->setObjectName(i ? "ptzVerticalSeek" : "ptzHorizontalSeek");
        advancedGrid->addWidget(seekSteps[i], i, 1);
    }
    rangeGrid->addWidget(advanced, 2, 0, 1, 2);
    readConfig = new QPushButton("读取配置", ranges);
    saveConfig = new QPushButton("保存并应用", ranges);
    rangeGrid->addWidget(readConfig, 3, 0);
    rangeGrid->addWidget(saveConfig, 3, 1);
    configNote = new QLabel("读取设备配置后修改；保存不会自动移动", ranges);
    configNote->setWordWrap(true);
    rangeGrid->addWidget(configNote, 4, 0, 1, 2);
    connect(readConfig, &QPushButton::clicked, this, &PtzPanel::requestConfig);
    connect(saveConfig, &QPushButton::clicked, this, [this] {
        QJsonObject params{{"expected", configSnapshot}};
        for (unsigned i = 0; i < 2; ++i)
            params.insert(i ? "v" : "h", QJsonObject{{"max_angle", maxAngle[i]->value()}, {"seek_steps", seekSteps[i]->value()}});
        configPending = true;
        configWait.restart();
        disable();
        configNote->setText("正在保存并应用…");
        emit command("ptz_set_config", params);
    });
    disable();
    timer = new QTimer(this);
    timer->setInterval(200);
    connect(timer, &QTimer::timeout, this, &PtzPanel::tick);
    timer->start();
}
void PtzPanel::disable()
{
    for (auto *b: directions)
        b->setEnabled(false);
    for (auto *b: move)
        b->setEnabled(false);
    home->setEnabled(false);
    center->setEnabled(false);
    readConfig->setEnabled(false);
    saveConfig->setEnabled(false);
}
void PtzPanel::requestConfig()
{
    configRequested = true;
    configPending = true;
    configWait.restart();
    disable();
    configNote->setText("正在读取配置…");
    emit command("ptz_get_config", {});
}
bool PtzPanel::applyConfig(const QJsonObject &c)
{
    if (!c.value("h").isObject() || !c.value("v").isObject()) {
        configSnapshot = {};
        configNote->setText("设备未返回有效行程配置");
        return false;
    }
    configSnapshot = c;
    for (unsigned i = 0; i < 2; ++i) {
        const auto a = c.value(i ? "v" : "h").toObject();
        maxAngle[i]->setValue(a.value("max_angle").toDouble());
        maxAngle[i]->setEnabled(true);
        seekSteps[i]->setValue(a.value("seek_steps").toInt());
    }
    return true;
}
void PtzPanel::begin(unsigned axis, bool inc)
{
    release(axis);
    auto &h = held[axis];
    h.token = QUuid::createUuid().toString(QUuid::WithoutBraces);
    h.increasing = inc;
    h.level = speed->currentData().toUInt();
    emit command("ptz_manual", {{"axis", axis ? "v" : "h"}, {"increasing", inc}, {"level", int(h.level)}, {"token", h.token}, {"renew", false}});
}
void PtzPanel::release(unsigned axis)
{
    if (held[axis].token.isEmpty())
        return;
    QString token = held[axis].token;
    held[axis].token.clear();
    emit command("ptz_release", {{"axis", axis ? "v" : "h"}, {"token", token}});
}
void PtzPanel::tick()
{
    if (!isVisible())
        return;
    if (configPending && configWait.elapsed() > 15000) {
        configPending = false;
        configSnapshot = {};
        configNote->setText("配置请求超时，保存结果未知，请重新读取");
    }
    if (fresh.isValid() && fresh.elapsed() > 2000) {
        release(0);
        release(1);
        disable();
        status->setText("云台状态超时，控制已暂停");
    }
    for (unsigned i = 0; i < 2; ++i) {
        const auto &h = held[i];
        if (h.token.isEmpty())
            continue;
        emit command("ptz_manual", {{"axis", i ? "v" : "h"}, {"increasing", h.increasing}, {"level", int(h.level)}, {"token", h.token}, {"renew", true}});
    }
    if (++ticks % 3 == 1)
        emit command("ptz_status", {});
}
void PtzPanel::receive(const QString &cmd, const QJsonObject &reply)
{
    if (cmd == "ptz_get_config_ack" || cmd == "ptz_set_config_ack") {
        if (reply.value("phase").toString() == "accepted")
            return;
        configPending = false;
        if (reply.value("result").toString() == "ok") {
            if (applyConfig(reply.value("ptz_config").toObject()))
                configNote->setText(cmd == "ptz_set_config_ack" ? "已保存并应用" : "已读取设备当前配置");
        } else {
            configSnapshot = {};
            configNote->setText(reply.value("error_msg").toString("配置操作失败，请重新读取"));
        }
        return;
    }
    if (reply.value("result").toString() != "ok") {
        error->setText(reply.value("error_msg").toString("云台命令失败"));
        if (cmd == "ptz_manual_ack") {
            release(0);
            release(1);
        }
        return;
    }
    if (cmd != "ptz_status_ack") {
        if (cmd != "ptz_manual_ack" && cmd != "ptz_release_ack")
            error->clear();
        return;  // 操作接受不代表到位；只用状态查询刷新显示
    }
    fresh.restart();
    const auto p = reply.value("ptz").toObject();
    if (!p.value("supported").toBool() || !p.value("available").toBool()) {
        release(0);
        release(1);
        disable();
        status->setText(p.value("supported").toBool() ? "云台配置或驱动不可用" : "固件未启用云台功能");
        return;
    }
    bool ready[2] = {false, false}, confirmed = true, calibrating = false, running = false;
    if (!defaultApplied) {
        int index = speed->findData(p.value("default_level").toInt(1));
        if (index >= 0)
            speed->setCurrentIndex(index);
        defaultApplied = true;
    }
    QStringList lines;
    for (unsigned i = 0; i < 2; ++i) {
        const auto a = p.value(i ? "v" : "h").toObject();
        const QString phase = a.value("phase").toString();
        bool busy = phase == "seeking" || phase == "centering";
        ready[i] = a.value("calibrated").toBool() && !busy && !configPending;
        running |= a.value("running").toBool();
        confirmed &= a.value("parameters_confirmed").toBool();
        calibrating |= busy;
        target[i]->setMaximum(a.value("max_steps").toInt());
        move[i]->setEnabled(ready[i]);
        QString state = phase == "seeking" ? "归零中" : phase == "centering" ? "回中中"
                : phase == "fault"                                           ? "故障"
                : ready[i]                                                   ? "已校准"
                                                                             : "未校准";
        lines << QString("%1：%2 → %3，%4%5")
                         .arg(i ? "垂直" : "水平")
                         .arg(a.value("position").toInteger())
                         .arg(a.value("target").toInteger())
                         .arg(state)
                         .arg(a.value("running").toBool() ? "，运行中" : "");
    }
    directions[0]->setEnabled(ready[0]);
    directions[1]->setEnabled(ready[0]);
    directions[2]->setEnabled(ready[1]);
    directions[3]->setEnabled(ready[1]);
    home->setEnabled(confirmed && !calibrating && !configPending);
    center->setEnabled(ready[0] && ready[1]);
    readConfig->setEnabled(!configPending);
    saveConfig->setEnabled(!configPending && !configSnapshot.isEmpty() && !calibrating && !running);
    if (!confirmed)
        lines << "归零方向和行程参数尚未确认";
    status->setText(lines.join("\n"));
    if (!configRequested)
        requestConfig();
}
void PtzPanel::shutdown()
{
    timer->stop();
    release(0);
    release(1);
    emit command("ptz_stop", {{"axis", "both"}});
}
void PtzPanel::hideEvent(QHideEvent *event)
{
    release(0);
    release(1);
    QWidget::hideEvent(event);
}
