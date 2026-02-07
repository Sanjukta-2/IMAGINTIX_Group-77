import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ArrowLeft, Upload, Palette } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const ColorProcessingUpload = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [colorMode, setColorMode] = useState<string>("true-color");

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        toast({
          title: "File too large",
          description: "Please upload an image smaller than 10MB",
          variant: "destructive",
        });
        return;
      }
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result as string);
        setProcessedImage(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleProcess = () => {
    if (!uploadedImage) {
      toast({
        title: "No image uploaded",
        description: "Please upload an image first",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);
    
    // Simulate processing
    setTimeout(() => {
      setProcessedImage(uploadedImage);
      setIsProcessing(false);
      toast({
        title: "Processing complete",
        description: `Your ${colorMode} image is ready`,
      });
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border">
        <div className="container mx-auto px-6 py-4">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-xl bg-secondary/10 mb-4">
              <Palette className="w-8 h-8 text-secondary" />
            </div>
            <h1 className="text-4xl font-bold text-foreground mb-4">
              Color Processing
            </h1>
            <p className="text-xl text-muted-foreground">
              Convert between true color and false color composites
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <Card className="p-6">
              <h2 className="text-xl font-semibold text-foreground mb-4">
                Upload Image
              </h2>
              <div className="space-y-4">
                <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-secondary/50 transition-colors">
                  <Input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                    id="image-upload"
                  />
                  <label
                    htmlFor="image-upload"
                    className="cursor-pointer flex flex-col items-center gap-2"
                  >
                    <Upload className="w-12 h-12 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">
                      Click to upload image
                    </span>
                    <span className="text-xs text-muted-foreground">
                      Max size: 10MB
                    </span>
                  </label>
                </div>

                {uploadedImage && (
                  <div className="space-y-4">
                    <img
                      src={uploadedImage}
                      alt="Uploaded"
                      className="w-full rounded-lg"
                    />
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-foreground">
                        Processing Mode
                      </label>
                      <Select value={colorMode} onValueChange={setColorMode}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="true-color">True Color</SelectItem>
                          <SelectItem value="false-color">False Color (Vegetation)</SelectItem>
                          <SelectItem value="false-color-urban">False Color (Urban)</SelectItem>
                          <SelectItem value="false-color-water">False Color (Water)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <Button
                      onClick={handleProcess}
                      disabled={isProcessing}
                      className="w-full"
                    >
                      {isProcessing ? "Processing..." : "Process Image"}
                    </Button>
                  </div>
                )}
              </div>
            </Card>

            <Card className="p-6">
              <h2 className="text-xl font-semibold text-foreground mb-4">
                Processed Result
              </h2>
              {processedImage ? (
                <div className="space-y-4">
                  <img
                    src={processedImage}
                    alt="Processed"
                    className="w-full rounded-lg"
                  />
                  <div className="p-3 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground">
                      Mode: <span className="font-medium text-foreground">{colorMode}</span>
                    </p>
                  </div>
                  <Button variant="outline" className="w-full">
                    Download Result
                  </Button>
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 border border-dashed border-border rounded-lg">
                  <p className="text-muted-foreground">
                    Processed image will appear here
                  </p>
                </div>
              )}
            </Card>
          </div>

          <Card className="p-6 bg-muted/50">
            <h3 className="font-semibold text-foreground mb-2">Note</h3>
            <p className="text-sm text-muted-foreground">
              This is a demonstration interface. Full color processing functionality 
              requires backend AI processing integration with satellite band data.
            </p>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default ColorProcessingUpload;
