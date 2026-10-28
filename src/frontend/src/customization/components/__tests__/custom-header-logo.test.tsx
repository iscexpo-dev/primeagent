import { render } from "@testing-library/react";
import CustomHeaderLogo from "../custom-header-logo";

jest.mock("@/assets/PrimeagentLogo.svg?react", () => ({
  __esModule: true,
  default: ({ className, ...props }: { className?: string }) => (
    <svg data-testid="primeagent-logo" className={className} {...props} />
  ),
}));

describe("CustomHeaderLogo", () => {
  it("renders the Primeagent logo by default", () => {
    const { getByTestId } = render(<CustomHeaderLogo />);

    expect(getByTestId("primeagent-logo")).toBeInTheDocument();
  });

  it("forwards the sizing class the header passes", () => {
    const { getByTestId } = render(<CustomHeaderLogo className="h-5 w-5" />);

    expect(getByTestId("primeagent-logo")).toHaveClass("h-5", "w-5");
  });

  // The surrounding button owns the accessible name, so the mark must not
  // announce a second one.
  it("stays hidden from assistive technology", () => {
    const { getByTestId } = render(<CustomHeaderLogo />);

    expect(getByTestId("primeagent-logo")).toHaveAttribute("aria-hidden", "true");
  });
});
