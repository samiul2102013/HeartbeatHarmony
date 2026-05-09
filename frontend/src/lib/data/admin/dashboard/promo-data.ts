// lib/data/promo-data.ts

export interface PromoItem {
  id: string;
  title: string;
  description: string;
  image: string;
  status: "active" | "inactive";
}

export const promoData: PromoItem[] = [
  {
    id: "1",
    title: "Summer Blockbuster Collection",
    description: "Control the promotional content on your production portal.",
    image: "https://www.figma.com/api/mcp/asset/27d85d2b-be0b-44ef-9ceb-7ba328753ed2",
    status: "active",
  },
  {
    id: "2",
    title: "Summer Blockbuster Collection",
    description: "Control the promotional content on your production portal.",
    image: "https://www.figma.com/api/mcp/asset/3c5107ee-dc9a-41a9-aec9-0c0ab9b0c8c0",
    status: "active",
  },
  {
    id: "3",
    title: "Summer Blockbuster Collection",
    description: "Control the promotional content on your production portal.",
    image: "https://www.figma.com/api/mcp/asset/513cba50-52d1-49ad-abb1-5a72f89022cd",
    status: "active",
  },
  {
    id: "4",
    title: "Summer Blockbuster Collection",
    description: "Control the promotional content on your production portal.",
    image: "https://www.figma.com/api/mcp/asset/95d70fd1-f7e5-4fe9-9086-6845b2d7e762",
    status: "active",
  },
  {
    id: "5",
    title: "Summer Blockbuster Collection",
    description: "Control the promotional content on your production portal.",
    image: "https://www.figma.com/api/mcp/asset/69351ca5-20bc-4aae-b3f8-50b109c3d266",
    status: "active",
  },
  {
    id: "6",
    title: "Summer Blockbuster Collection",
    description: "Control the promotional content on your production portal.",
    image: "https://www.figma.com/api/mcp/asset/e3c61a82-8ae4-4e51-909f-f67a50461826",
    status: "active",
  },
];