import React from 'react';
import { Button } from './button';
import { RocketLaunchIcon } from '@heroicons/react/24/outline';
import type { Screenshot, ScreenshotsProps } from '@/types/screenshots';
import screenshotsDemoCollection from '@/fixtures/screenshotsDemoCollection';

const defaultScreenshots = screenshotsDemoCollection;

const ScreenshotsDemo: React.FC<ScreenshotsProps> = ({
  screenshots = defaultScreenshots,
}) => {
  return (
    <div className="w-full">
      <div className="flex justify-between items-center pb-10">
        <div>
          <h2 className="text-2xl font-bold pb-3">Скриншоты продукта</h2>
          <p className="text-gray-700">
            Дашборды, подборки, ИИ-чат и мониторинг - готово из коробки.
          </p>
        </div>
        <Button className="bg-blue-500">
          <RocketLaunchIcon />
          Открыть демо
        </Button>
      </div>
      <div>
        <ul className="flex flex-wrap gap-5">
          {screenshots.map((item: Screenshot) => (
            <li
              key={item.name}
              className="h-100 w-100 border rounded-xl bg-white relative"
            >
              <img
                src={item.image}
                alt=""
                className="absolute inset-0 w-full h-full object-cover rounded-xl"
              />
              <a href="" className="absolute bottom-5 left-5">
                {item.name}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ScreenshotsDemo;
