"use client";

import { useState } from "react";
import SearchBar from "./searchBar";

function TitleComponent() {
  const [search, setSearch] = useState("");
  return (
    <div className="flex justify-center items-center h-full overflow-hidden pb-56">
      <div className="flex gap-10 flex-col">
        <h1 className="text-5xl font-bold text-center mt-20 text-[#9ABFFF]">
          Welcome to Leap Code
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
