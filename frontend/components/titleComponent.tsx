"use client";

import { useState } from "react";
import SearchBar from "./searchBar";
import { Arima } from "next/font/google";

const arima = Arima({
  subsets: ["latin"],
  weight: "variable",
});

function TitleComponent() {
  const [search, setSearch] = useState("");
  return (
    <div className="flex justify-center items-center h-full overflow-hidden pb-56">
      <div className="flex gap-10 flex-col">
        <h1
          className={`text-8xl font-bold text-center mt-20 text-[#9ABFFF] ${arima.className}`}
        >
          <span className="text-[#3C6E71]">LEAP</span>
          <span className="text-white">Code</span>
        </h1>
        <SearchBar search={search} setSearch={setSearch} />
        <div className="flex justify-center">
          <button className="bg-[#0069FF] text-white px-8 py-3 text-xs">
            Search Now
          </button>
        </div>
      </div>
    </div>
  );
}
export default TitleComponent;
