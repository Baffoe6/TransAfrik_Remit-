import { secureStorage } from "./secureStorage";

export async function getDevicePayload() {
  const device_id = await secureStorage.getOrCreateDeviceId();
  return { device_id, device_label: "TransAfrik Mobile" };
}
