#include "device/ui/ptzpanel.h"
#include <QApplication>
#include <QPushButton>
#include <QComboBox>
#include <QDoubleSpinBox>
#include <QSpinBox>
#include <QEventLoop>
#include <QTimer>
#include <QJsonArray>
#include <cstdio>
#include <cstdlib>
static void check(bool b)
{
    if (!b)
        std::abort();
}
static void wait(int ms)
{
    QEventLoop loop;
    QTimer::singleShot(ms, &loop, &QEventLoop::quit);
    loop.exec();
}
int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    PtzPanel p;
    p.show();
    QStringList commands;
    QList<QJsonObject> params;
    QObject::connect(&p, &PtzPanel::command, [&](const QString &c, const QJsonObject &v) {commands<<c;params<<v; });
    QPushButton *left = nullptr;
    for (auto *b: p.findChildren<QPushButton *>())
        if (b->text() == "←")
            left = b;
    check(left && !left->isEnabled());
    QJsonObject axis{{"calibrated", true}, {"parameters_confirmed", true}, {"phase", "ready"}, {"max_steps", 4039}, {"position", 2020}, {"target", 2020}};
    QJsonObject state{{"supported", true}, {"available", true}, {"h", axis}, {"v", axis}};
    p.receive("ptz_status_ack", {{"result", "ok"}, {"ptz", state}});
    check(commands.last() == "ptz_get_config");
    QJsonObject h{{"max_angle", 355.0}, {"seek_steps", 4200}}, v{{"max_angle", 90.0}, {"seek_steps", 1100}};
    QJsonObject config{{"h", h}, {"v", v}};
    p.receive("ptz_get_config_ack", {{"result", "ok"}, {"phase", "completed"}, {"ptz_config", config}});
    p.receive("ptz_status_ack", {{"result", "ok"}, {"ptz", state}});
    auto *angle = p.findChild<QDoubleSpinBox *>("ptzHorizontalAngle");
    check(angle && angle->value() == 355.0);
    angle->setValue(180.0);
    p.receive("ptz_status_ack", {{"result", "ok"}, {"ptz", state}});
    check(angle->value() == 180.0);  // 周期状态不能覆盖正在编辑的行程。
    for (auto *b: p.findChildren<QPushButton *>())
        if (b->text() == "保存并应用")
            b->click();
    check(commands.last() == "ptz_set_config" && params.last()["h"].toObject()["max_angle"].toDouble() == 180.0);
    check(params.last()["h"].toObject()["seek_steps"].toInt() == 4200);
    check(params.last()["expected"].toObject() == config && !left->isEnabled());
    p.receive("ptz_set_config_ack", {{"result", "ok"}, {"phase", "accepted"}});
    check(!left->isEnabled());
    p.receive("ptz_set_config_ack", {{"result", "ok"}, {"phase", "completed"}, {"ptz_config", config}});
    p.receive("ptz_status_ack", {{"result", "ok"}, {"ptz", state}});
    check(left->isEnabled());
    p.findChild<QComboBox *>()->setCurrentIndex(3);
    for (auto *b: p.findChildren<QPushButton *>())
        if (b->text() == "校准并回中")
            b->click();
    check(commands.last() == "ptz_home" && params.last()["level"].toInt() == 4);
    QMetaObject::invokeMethod(left, "pressed");
    check(commands.last() == "ptz_manual" && !params.last()["renew"].toBool());
    const QString token = params.last()["token"].toString();
    check(!token.isEmpty());
    wait(250);
    bool renewed = false;
    for (int i = 0; i < commands.size(); ++i)
        if (commands[i] == "ptz_manual" && params[i]["renew"].toBool())
            renewed = params[i]["token"].toString() == token;
    check(renewed);
    QMetaObject::invokeMethod(left, "released");
    check(commands.last() == "ptz_release" && params.last()["token"].toString() == token);
    QMetaObject::invokeMethod(left, "pressed");
    p.hide();
    check(commands.last() == "ptz_release");
    p.show();
    p.receive("ptz_status_ack", {{"result", "ok"}, {"ptz", QJsonObject{{"supported", false}}}});
    check(!left->isEnabled());
    p.shutdown();
    check(commands.last() == "ptz_stop");
    puts("PASS: PTZ UI capability gating, hold/renew/release token, hide and close stop");
}
