import dotenv from "dotenv";
import fs from "fs";
import path from "path";

export function loadDotenvIfLocal(dir: string): void {
  const candidates = [
    path.resolve(dir, "..", "..", "..", "..", ".env"),
    path.resolve(process.cwd(), ".env"),
    path.resolve(process.cwd(), "..", ".env"),
  ];
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      dotenv.config({ path: candidate });
      return;
    }
  }
}
