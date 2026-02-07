import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { CloudOff, Palette, ChevronDown, Menu, Sun, Moon, Monitor } from "lucide-react";
import { useTheme } from "next-themes";
import satelliteImage from "@/assets/satellite-earth.jpg";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const Index = () => {
  const navigate = useNavigate();
  const scrollTargetRef = useRef<HTMLDivElement>(null);
  const { setTheme, theme } = useTheme();

  const scrollToOptions = () => {
    scrollTargetRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    const handleScroll = () => {
      const scrolled = window.scrollY;
      const parallax = document.getElementById("parallax-bg");
      if (parallax) {
        parallax.style.transform = `translateY(${scrolled * 0.5}px)`;
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section with Sign In */}
      <section className="relative h-screen overflow-hidden">
        <div
          id="parallax-bg"
          className="absolute inset-0 w-full h-[120%] bg-cover bg-center"
          style={{
            backgroundImage: `url(${satelliteImage})`,
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-background/70 via-background/50 to-background" />
        </div>

        <div className="relative z-10 h-full flex flex-col">
          <header className="p-6 flex justify-between items-center">
            <Button
              variant="ghost"
              className="text-foreground hover:text-primary hover:bg-primary/10 font-semibold text-lg"
            >
              Sign In
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="text-foreground hover:text-primary hover:bg-primary/10 font-semibold text-lg gap-2"
                >
                  <Menu className="w-5 h-5" />
                  Menu
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem className="cursor-pointer">
                  Contact Us
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer">
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer">
                  News
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuSub>
                  <DropdownMenuSubTrigger className="cursor-pointer">
                    {theme === "light" && <Sun className="w-4 h-4 mr-2" />}
                    {theme === "dark" && <Moon className="w-4 h-4 mr-2" />}
                    {theme === "system" && <Monitor className="w-4 h-4 mr-2" />}
                    Theme
                  </DropdownMenuSubTrigger>
                  <DropdownMenuSubContent>
                    <DropdownMenuItem onClick={() => setTheme("light")} className="cursor-pointer">
                      <Sun className="w-4 h-4 mr-2" />
                      Light
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setTheme("dark")} className="cursor-pointer">
                      <Moon className="w-4 h-4 mr-2" />
                      Dark
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setTheme("system")} className="cursor-pointer">
                      <Monitor className="w-4 h-4 mr-2" />
                      System
                    </DropdownMenuItem>
                  </DropdownMenuSubContent>
                </DropdownMenuSub>
              </DropdownMenuContent>
            </DropdownMenu>
          </header>

          <div className="flex-1 flex flex-col items-center justify-center text-center px-6 pb-20">
            <h1 className="text-6xl md:text-7xl font-bold text-foreground mb-6 tracking-tight">
              Satellite Imagery
              <br />
              <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                Processing
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mb-8">
              Advanced tools for cloud removal and color enhancement of satellite data
            </p>
            <Button
              onClick={scrollToOptions}
              size="lg"
              className="gap-2 bg-primary hover:bg-primary/90 text-primary-foreground shadow-[var(--glow-primary)]"
            >
              Explore Tools
              <ChevronDown className="w-5 h-5 animate-bounce" />
            </Button>
          </div>
        </div>
      </section>

      {/* Processing Options Section */}
      <section ref={scrollTargetRef} className="py-20 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-foreground mb-4">
              Choose Your Processing Type
            </h2>
            <p className="text-xl text-muted-foreground">
              Select the tool that best fits your analysis needs
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Cloud Removal Card */}
            <div className="group relative overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-card to-card/50 p-8 transition-all hover:shadow-[var(--glow-primary)] hover:border-primary/50">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-3xl transition-all group-hover:bg-primary/20" />
              
              <div className="relative">
                <div className="w-16 h-16 rounded-xl bg-primary/10 flex items-center justify-center mb-6 group-hover:bg-primary/20 transition-colors">
                  <CloudOff className="w-8 h-8 text-primary" />
                </div>
                
                <h3 className="text-3xl font-bold text-foreground mb-4">
                  Cloud Removal
                </h3>
                
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-foreground mb-3">How It Works</h4>
                  <p className="text-muted-foreground leading-relaxed">
                    Remove cloud cover from satellite imagery using advanced AI algorithms. 
                    Perfect for obtaining clear views of terrain and infrastructure.
                  </p>
                </div>

                <Button
                  onClick={() => navigate("/cloud-removal-upload")}
                  className="w-full gap-2"
                >
                  <CloudOff className="w-4 h-4" />
                  Upload Image to Get De-clouded Image
                </Button>
              </div>
            </div>

            {/* True/False Color Card */}
            <div className="group relative overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-card to-card/50 p-8 transition-all hover:shadow-[var(--glow-secondary)] hover:border-secondary/50">
              <div className="absolute top-0 right-0 w-32 h-32 bg-secondary/10 rounded-full blur-3xl transition-all group-hover:bg-secondary/20" />
              
              <div className="relative">
                <div className="w-16 h-16 rounded-xl bg-secondary/10 flex items-center justify-center mb-6 group-hover:bg-secondary/20 transition-colors">
                  <Palette className="w-8 h-8 text-secondary" />
                </div>
                
                <h3 className="text-3xl font-bold text-foreground mb-4">
                  True Color & False Color
                </h3>
                
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-foreground mb-3">How It Works</h4>
                  <p className="text-muted-foreground leading-relaxed">
                    Convert imagery between natural and enhanced color composites. 
                    Reveal vegetation health, water content, and hidden features.
                  </p>
                </div>

                <Button
                  onClick={() => navigate("/color-processing-upload")}
                  variant="secondary"
                  className="w-full gap-2"
                >
                  <Palette className="w-4 h-4" />
                  Upload Image for Color Processing
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;