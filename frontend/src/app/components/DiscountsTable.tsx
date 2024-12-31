import Link from "next/link";

interface DiscountsTableProps {
  convenios: Convenio[];
  sortBy: string;
  order: string;
  onSort: (field: string) => void;
}

function DiscountsTable({
  convenios,
  sortBy,
  order,
  onSort,
}: DiscountsTableProps) {
  const getSortIcon = (field: string) => {
    if (sortBy === field) {
      return order === "asc" ? "▲" : "▼";
    }
    return null;
  };

  return (
    <table className="table-auto w-full border-collapse border border-gray-300 mt-4">
      <thead>
        <tr className="bg-gray-200">
          <th
            className="border border-gray-300 px-4 py-2 text-black cursor-pointer"
            onClick={() => onSort("title")}
            style={{ width: "30%" }}
          >
            Título {getSortIcon("title")}
          </th>
          <th
            className="border border-gray-300 px-4 py-2 text-black cursor-pointer"
            style={{ width: "40%" }}
          >
            Desconto
          </th>
          <th
            className="borderborder-gray-300 px-4 py-2 text-black cursor-pointer"
            onClick={() => onSort("cats")}
            style={{ width: "20%" }}
          >
            Categorias {getSortIcon("cats")}
          </th>
          <th
            className="border border-gray-300 px-4 py-2 text-black cursor-pointer"
            onClick={() => onSort("date")}
            style={{ width: "20%" }}
          >
            Data {getSortIcon("date")}
          </th>
        </tr>
      </thead>
      <tbody>
        {convenios.map((item: Convenio) => (
          <tr key={item.id} className="hover:bg-gray-100 cursor-pointer">
            <td className="border border-gray-300 px-4 py-2">
              <Link
                href={`/convenios/${item.id}`}
                className="text-blue-500 hover:underline"
              >
                {item.title}
              </Link>
            </td>
            <td className="border border-gray-300 px-4 py-2">
              {item.discounts}
            </td>
            <td className="border border-gray-300 px-4 py-2">
              {item.cats.split(", ").map((cat, index) => (
                <span key={index}>
                  <Link
                    href={`/categoria/${cat.toLowerCase().replace(" ", "-")}`}
                    className="text-blue-500 hover:underline"
                  >
                    {cat}
                  </Link>
                  {index < item.cats.split(", ").length - 1 && ", "}
                </span>
              ))}
            </td>
            <td className="border border-gray-300 px-4 py-2">
              {new Date(item.date).toLocaleDateString()}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default DiscountsTable;
