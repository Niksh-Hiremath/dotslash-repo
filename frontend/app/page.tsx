import HomeDecoration from "@/components/homeDecoration";
import NavBar from "@/components/navBar";
import TitleComponent from "@/components/titleComponent";
export default function Home() {
  return (
    <div className="h-full">
      <NavBar home={true} />
      <HomeDecoration />
      <TitleComponent />
    </div>
  );
}
