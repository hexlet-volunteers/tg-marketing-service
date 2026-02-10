import React from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useMediaQuery } from 'react-responsive';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import ChannelCard from '../ui/ChannelCard.tsx';
import type { Channel, ChannelsProps } from '@/types/channel.ts';
import formatNumberShort from '@/utils/formatNumberShort.ts';
import {
  reduceChannelsByCategory,
  countChannelsByCategory,
  mapCategoryCountEntry,
} from '@/utils/reduceChannels.ts';
import channelsCol from '@/fixtures/channelsCollection.ts';
import { CheckIcon } from '@heroicons/react/24/outline';

const defaultChannels = channelsCol;

const Channels: React.FC<ChannelsProps> = ({ channels = defaultChannels }) => {
  const isMobile = useMediaQuery({ maxWidth: 767 });
  const isTablet = useMediaQuery({ minWidth: 768, maxWidth: 1023 });
  const countries: string[] = [
    ...new Set(channels.map(({ country }) => country)),
  ];

  const channelsByCategory = Object.entries(
    channels.reduce<Record<string, Channel[]>>(reduceChannelsByCategory, {})
  );

  const categoriesCountObj = channels.reduce(countChannelsByCategory, {});

  const categoriesCounter = Object.entries(categoriesCountObj).map(
    mapCategoryCountEntry
  );

  const categories =
    isMobile || isTablet
      ? categoriesCounter.slice(0, isMobile ? 3 : 12)
      : categoriesCounter.slice(0, 12);

  const isVerifChannels = channels.filter((channel) => channel.verified);

  const channelsForVerif =
    isMobile || isTablet
      ? isVerifChannels.slice(0, isMobile ? 2 : 4)
      : isVerifChannels.slice(0, 6);

  return (
    <div className="w-full bg-gray-50 flex justify-center">
      <div className="max-w-xs md:max-w-2xl lg:max-w-4xl xl:max-w-7xl mx-auto py-20 px-5">
        <div className="flex justify-center">
          <h1 className="text-xl md:text-2xl lg:text-4xl font-bold">
            Каталог подборок Telegram
          </h1>
        </div>
        <div className="pt-10 flex flex-col md:flex-row items-center justify-center gap-5">
          <Select>
            <SelectTrigger className="w-[250px] lg:w-[300px] text-sm md:text-base">
              <SelectValue placeholder="Выберите страну" />
            </SelectTrigger>
            <SelectContent>
              {countries.map((country) => (
                <SelectItem
                  key={country}
                  value={`${country}`}
                >{`${country}`}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Input
            className="w-[250px] lg:w-[450px] text-sm md:text-base"
            type="search"
            placeholder="Поиск по подборкам"
          />
          <Button
            variant="outline"
            className="cursor-pointer w-[250px] md:w-[100px]"
          >
            Найти
          </Button>
        </div>
        <ul className="flex flex-col flex-wrap md:flex-nowrap md:flex-row items-center justify-center gap-5 py-10">
          {channels.slice(0, 3).map((channel) => (
            <li key={channel.id} className="w-70 md:w-1/3 xl:w-100">
              <ChannelCard channel={channel} height="25" />
            </li>
          ))}
        </ul>
        <div className="flex flex-col my-5 items-center md:items-start">
          <div className="flex gap-3 items-center justify-start pb-5">
            <h2 className="text-md md:text-xl lg:text-2xl font-bold ">
              Верифицированные подборки
            </h2>
            <CheckIcon className="size-5 md:size-6 text-blue-500"/>
          </div>
          <div className="w-full p-5 h-55 py-5 border flex flex-col md:flex-row items-center justify-center gap-5 bg-background rounded-md shadow-md">
            <ul className="w-full grid md:grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {channelsForVerif.map((channel) => (
                <li key={channel.id} className="flex-1 w-60 md:w-70 lg:w-full">
                  <ChannelCard channel={channel} height="20" />
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="flex flex-col my-5 items-center md:items-start">
          <div className="flex gap-3 items-center py-5">
            <h2 className="text-md md:text-xl lg:text-2xl font-bold">
              Все категории
            </h2>
          </div>
          <div className="w-full p-5 h-55 py-5 border flex flex-col md:flex-row items-center justify-center gap-5 bg-background rounded-md shadow-md">
            <ul className="w-full grid grid-cols-1 md:grid-cols-4 gap-3">
              {categories.map(({ category, count }) => (
                <li key={category} className="flex-1">
                  <div
                    className={`h-10 flex items-center justify-between p-2 px-5 gap-2 border bg-background rounded-md shadow-xs flex-nowrap`}
                  >
                    <a href="" className="font-medium truncate">
                      {category}
                    </a>
                    <p className="text-xs text-gray-500">
                      {formatNumberShort(count)}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <ul>
          {channelsByCategory.map(([category, chList]) => (
            <li key={category}>
              <div className="flex flex-col my-5 items-center md:items-start">
                <div className="w-full flex flex-row items-center justify-between py-5">
                  <h3 className="text-md md:text-xl lg:text-2xl font-bold">
                    {category}
                  </h3>
                  <a href="" className="text-sm font-semibold px-3">
                    Ещё
                  </a>
                </div>
                <div className="w-full p-5 h-50 md:h-30 py-5 border flex flex-col md:flex-row items-center justify-center gap-5 bg-background rounded-md shadow-md">
                  <ul className="w-full grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {isMobile || isTablet
                      ? chList.slice(0, isMobile ? 2 : 3).map((channel) => (
                          <li key={channel.id} className="w-60 md:w-full">
                            <ChannelCard channel={channel} height="20" />
                          </li>
                        ))
                      : chList.slice(0, 4).map((channel) => (
                          <li key={channel.id} className="w-60 md:w-full">
                            <ChannelCard channel={channel} height="20" />
                          </li>
                        ))}
                  </ul>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Channels;
