// Kayar engel plugin'i: modeli dunya cercevesinde Y ekseni boyunca sabit
// hizla iki limit arasinda gidip gelecek sekilde tasir (ucgen dalga -
// gercek motor+zincir tahriki gibi). Joint kullanmaz; kinematic modeli
// SetWorldPose ile surer.
// SDF parametreleri: <hiz> (m/s), <alt> (m), <ust> (m) - baslangic konumuna
// gore ofset araligi.
#include <cmath>

#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <ignition/math/Pose3.hh>

namespace gazebo
{
class KayarEngelPlugin : public ModelPlugin
{
public:
  void Load(physics::ModelPtr _model, sdf::ElementPtr _sdf) override
  {
    this->model = _model;
    if (_sdf->HasElement("hiz"))
      this->hiz = _sdf->Get<double>("hiz");
    if (_sdf->HasElement("alt"))
      this->alt = _sdf->Get<double>("alt");
    if (_sdf->HasElement("ust"))
      this->ust = _sdf->Get<double>("ust");

    this->basPoz = this->model->WorldPose();
    this->conn = event::Events::ConnectWorldUpdateBegin(
        std::bind(&KayarEngelPlugin::OnUpdate, this));
    gzmsg << "KayarEngelPlugin yuklendi: hiz=" << this->hiz
          << " m/s, aralik=[" << this->alt << ", " << this->ust << "] m\n";
  }

private:
  void OnUpdate()
  {
    const double t = this->model->GetWorld()->SimTime().Double();
    const double yol = this->ust - this->alt;
    const double faz = std::fmod(this->hiz * t, 2.0 * yol);
    const double ofset = this->alt + (faz < yol ? faz : 2.0 * yol - faz);

    ignition::math::Pose3d poz = this->basPoz;
    poz.Pos().Y() += ofset;
    this->model->SetWorldPose(poz);
  }

  physics::ModelPtr model;
  event::ConnectionPtr conn;
  ignition::math::Pose3d basPoz;
  double hiz = 0.2;   // m/s
  double alt = -2.2;  // m
  double ust = 1.8;   // m
};

GZ_REGISTER_MODEL_PLUGIN(KayarEngelPlugin)
}  // namespace gazebo
