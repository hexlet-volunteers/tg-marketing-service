interface Screenshot {
  name: string;
  image: string;
}

interface ScreenshotsProps {
  screenshots: Screenshot[];
}

export type { Screenshot, ScreenshotsProps };
