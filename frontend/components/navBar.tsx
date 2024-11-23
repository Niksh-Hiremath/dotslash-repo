import Image from "next/image";

function NavBar({ home }: { home: boolean }) {
  return (
    <nav className="flex p-4 bg-[#CED4DA] items-center justify-between w-full">
      <div className="flex items-center gap-20">
        <div className="flex items-center gap-2">
          <Image src="/logo.png" alt="Logo" width={36} height={36} />
          <p>LEAP CODE</p>
        </div>
        <div className="flex gap-12">
          <a
            href="#"
            className={
              "text-sm " + (home ? "underline text-[#3E5C76] font-bold" : "")
            }
          >
            Home
          </a>
          <a
            href="#"
            className={
              "text-sm" + (!home ? "underline text-[#3E5C76] font-bold" : "")
            }
          >
            Previous Problems
          </a>
        </div>
      </div>
      <div className="flex gap-4">
        <button className="bg-[#3E5C76] text-white px-16 py-1 rounded-lg text-xs">
          Log In
        </button>
        <button className="bg-[#3E5C76] text-white px-16 py- rounded-lg text-xs">
          Sign Up
        </button>
        <Image src="/logo.png" alt="Logo" width={36} height={36} />
      </div>
    </nav>
  );
}
export default NavBar;
