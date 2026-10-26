#pragma once
#include <QWidget>
#include <QJsonObject>
#include <QElapsedTimer>
class QLabel;
class QPushButton;
class QComboBox;
class QSpinBox;
class QDoubleSpinBox;
class QTimer;
class PtzPanel: public QWidget
{
    Q_OBJECT
  public:
    explicit PtzPanel(QWidget *parent = nullptr);
    void receive(const QString &command, const QJsonObject &reply);
    void shutdown();
  signals:
    void command(const QString &name, const QJsonObject &params);

  protected:
    void hideEvent(QHideEvent *event) override;

  private:
    void tick();
    void release(unsigned axis);
    void begin(unsigned axis, bool increasing);
    void disable();
    void requestConfig();
    bool applyConfig(const QJsonObject &config);
    struct Hold {
        QString token;
        bool increasing = false;
        unsigned level = 1;
    };
    Hold held[2];
    QComboBox *speed;
    QSpinBox *target[2];
    QDoubleSpinBox *maxAngle[2];
    QSpinBox *seekSteps[2];
    QPushButton *readConfig, *saveConfig;
    QLabel *configNote;
    QJsonObject configSnapshot;
    QElapsedTimer configWait;
    bool configPending = false, configRequested = false;
    QPushButton *directions[4], *move[2], *home, *center;
    QLabel *status, *error;
    QTimer *timer;
    QElapsedTimer fresh;
    unsigned ticks = 0;
    bool defaultApplied = false;
};
