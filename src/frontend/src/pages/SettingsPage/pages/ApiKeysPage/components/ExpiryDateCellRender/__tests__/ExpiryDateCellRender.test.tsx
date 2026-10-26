import { render, screen } from "@testing-library/react";
import type { CustomCellRendererProps } from "ag-grid-react";
import { TooltipProvider } from "@/components/ui/tooltip";
import ExpiryDateCellRender from "../index";

jest.mock("@/components/core/dateReaderComponent", () => ({
  __esModule: true,
  default: ({ date }: { date: string }) => (
    <span data-testid="date-reader">{date}</span>
  ),
}));

const renderWithProvider = (ui: React.ReactElement) =>
  render(<TooltipProvider>{ui}</TooltipProvider>);

describe("ExpiryDateCellRender", () => {
  it("renders DateReader when a date value is provided", () => {
    const props = {
      value: "2025-06-01T00:00:00Z",
      node: undefined,
    } as unknown as CustomCellRendererProps;
    renderWithProvider(<ExpiryDateCellRender {...props} />);
    expect(screen.getByTestId("date-reader")).toBeInTheDocument();
    expect(screen.getByTestId("date-reader")).toHaveTextContent(
      "2025-06-01T00:00:00Z",
    );
  });

  it("renders infinity symbol when value is null", () => {
    const props = { value: null, node: undefined } as unknown as CustomCellRendererProps;
    renderWithProvider(<ExpiryDateCellRender {...props} />);
    expect(screen.getByText("∞")).toBeInTheDocument();
    expect(screen.queryByTestId("date-reader")).not.toBeInTheDocument();
  });

  it("renders infinity symbol when value is undefined", () => {
    const props = { value: undefined, node: undefined } as unknown as CustomCellRendererProps;
    renderWithProvider(<ExpiryDateCellRender {...props} />);
    expect(screen.getByText("∞")).toBeInTheDocument();
    expect(screen.queryByTestId("date-reader")).not.toBeInTheDocument();
  });

  it("renders infinity symbol when value is an empty string", () => {
    const props = { value: "", node: undefined } as unknown as CustomCellRendererProps;
    renderWithProvider(<ExpiryDateCellRender {...props} />);
    expect(screen.getByText("∞")).toBeInTheDocument();
  });
});
