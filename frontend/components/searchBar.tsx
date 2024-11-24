"use client";

import Image from "next/image";

function SearchBar({
  search,
  setSearch,
}: {
  search: string;
  setSearch: React.Dispatch<React.SetStateAction<string>>;
}) {
  return (
    <div className="flex justify-center w-full focus-within:border-[#0069FF] border border-solid rounded-full px-2 py-2 gap-2">
      {/* <Image src="/logo.png" width={36} height={36} alt="Search icon" /> */}

      <input
        type="text"
        placeholder="Enter LeetCode problem number..."
        value={search}
        onChange={(event) => {
          setSearch(event.target.value);
        }}
        className="border-2 border-[#3E5C76] rounded-lg w-full bg-transparent text-white border-none focus:outline-none pl-3"
      />
    </div>
  );
}

export default SearchBar;
