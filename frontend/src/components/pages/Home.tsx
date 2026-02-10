import React from 'react';
import ScreenshotsDemo from '../ui/ScreenshotsDemo';
import screenshotsDemoColl from '@/fixtures/screenshotsDemoCollection';

const Home: React.FC = () => {
  return (
    <div className="w-full bg-blue-50 items-center justify-center">
      <div className="w-full h-150 bg-linear-to-t from-white to-blue-50 flex justify-center">
        <div className="max-w-xs md:max-w-2xl lg:max-w-4xl xl:max-w-7xl mx-auto py-20 px-5">
          <div className="h-100 w-full flex gap-5 pb-10">
            <div>
              <h1 className="py-5 text-4xl font-bold">
                Аналитика Telegram + тренды +
                <span className="text-blue-500"> ИИ-помощник</span>
              </h1>
            </div>
            <div className="h-full w-200 bg-gray-100 border-2">
              TG Analytics Dashboard
            </div>
          </div>
        </div>
      </div>

      <div className="w-full bg-gray-50">
        <div className="max-w-xs md:max-w-2xl lg:max-w-4xl xl:max-w-7xl mx-auto py-20 px-5">
          <ScreenshotsDemo screenshots={screenshotsDemoColl}/>
        </div>
      </div>
    </div>
  );
};

export default Home;
