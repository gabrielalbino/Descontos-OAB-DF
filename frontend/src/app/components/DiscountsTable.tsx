import { SortAscIcon, SortDescIcon } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

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
      return order === "asc" ? <SortAscIcon /> : <SortDescIcon />;
    }
    return null;
  };

  const Header = ({
    field,
    label,
    onSort,
    width,
    colspan = 1,
    sortable = true,
  }: {
    field: string;
    label: string;
    onSort: (field: string) => void;
    width: string;
    colspan?: number;
    sortable?: boolean;
  }) => (
    <th
      className="border border-gray-300 px-4 py-2 text-black cursor-pointer"
      onClick={() => (sortable ? onSort(field) : null)}
      style={{ width, minWidth: width, maxWidth: width }}
      colSpan={colspan}
    >
      <span className="text-sm font-semibold flex items-center justify-between space-x-2">
        {label} {sortable ? getSortIcon(field) : null}
      </span>
    </th>
  );

  return (
    <table className="table-auto w-full border-collapse border border-gray-300 mt-4">
      <thead>
        <tr className="bg-gray-200">
          <Header
            field="title"
            label="Título"
            onSort={onSort}
            width="30%"
            colspan={2}
          />
          <Header
            field="discounts"
            label="Desconto"
            sortable={false}
            onSort={onSort}
            width="40%"
          />
          <Header field="cats" label="Categorias" onSort={onSort} width="20%" />
          <Header field="date" label="Data" onSort={onSort} width="20%" />
        </tr>
      </thead>
      <tbody>
        {convenios?.map((item: Convenio) => (
          <tr key={item.id} className="hover:bg-gray-100 cursor-pointer">
            <td className="border border-gray-300 p-0">
              <img
                src={item.image}
                alt={item.title}
                className="w-full h-full object-cover"
              />
            </td>
            <td className="border border-gray-300 px-4 py-2">
              <Link
                href={`/convenios/${item.id}`}
                className="text-blue-500 hover:underline flex items-center space-x-2"
              >
                <div
                  dangerouslySetInnerHTML={{ __html: item.title_highlight }}
                />
              </Link>
            </td>
            <td className="border border-gray-300 px-4 py-2">
              {/* {item.discounts} */}
              <div
                dangerouslySetInnerHTML={{ __html: item.discounts_highlight }}
              ></div>
            </td>
            <td className="border border-gray-300 px-4 py-2">
              {item.cats.split(", ").map((cat, index) => (
                <span key={index}>
                  <Link
                    href={`/categoria/${cat}`}
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
