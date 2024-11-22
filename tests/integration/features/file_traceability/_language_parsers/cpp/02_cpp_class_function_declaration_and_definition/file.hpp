class EcuHal
{
  public:
    // @relation(REQ-1, scope=function)
    bool CanSend(const CanFrame &frame);
};
